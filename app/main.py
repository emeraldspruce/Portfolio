# app/main.py
from fastapi import FastAPI, Request, BackgroundTasks, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .content_loader import load_json
from .models import Base, Contact, Message, ResumeDownload
from .emailer import notify_new_contact
from dotenv import load_dotenv
import os

# ===============================
# Database
# ===============================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///portfolio.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

# ===============================
# FastAPI
# ===============================
app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Content
HOME = load_json("home.json")
ABOUT = load_json("about.json")
PROJECTS = load_json("projects.json")
CONTACT_ME = load_json("contact_me.json")

PROJECT_LIST = PROJECTS.get("projects", [])
PROJECT_BY_SLUG = {p["slug"]: p for p in PROJECT_LIST}

# -------------------------------
# Main Pages
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "content": HOME,
        "projects": PROJECT_LIST,  # for featured list
    })

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "content": ABOUT})

@app.get("/projects", response_class=HTMLResponse)
def projects(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request, "content": PROJECTS})

@app.get("/contact_me", response_class=HTMLResponse)
def contact_me(request: Request):
    # Renders the form; submission handled by /api/contact_me via HTMX
    return templates.TemplateResponse("contact_me.html", {"request": request, "content": CONTACT_ME})

# -------------------------------
# Unique project pages
# -------------------------------
@app.get("/projects/{slug}", response_class=HTMLResponse)
def project_detail(slug: str, request: Request):
    project = PROJECT_BY_SLUG.get(slug)
    if not project:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "project": project}
    )

# -------------------------------
# HTMX endpoint for contact form
# -------------------------------
@app.post("/api/contact_me", response_class=HTMLResponse)
def submit_contact(
    request: Request,
    bg: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    requested_transcript: bool = Form(False),
    db: Session = Depends(get_db),
):
    # Upsert contact
    contact = db.query(Contact).filter(Contact.email == email).one_or_none()
    if not contact:
        contact = Contact(name=name, email=email)
        db.add(contact)
        db.flush()

    # Store message
    msg = Message(contact_id=contact.id, body=message, requested_transcript=bool(requested_transcript))
    db.add(msg)
    db.commit()

    # Notify via email in background
    bg.add_task(notify_new_contact, name, email, requested_transcript, message)

    # Return a small partial for HTMX to swap into the page
    return templates.TemplateResponse("_contact_result.html", {"request": request, "ok": True})

# -------------------------------
# Resume page
# -------------------------------
@app.get("/resume", response_class=FileResponse)
def resume(request: Request, db: Session = Depends(get_db)):
    db.add(ResumeDownload(ip=request.client.host, user_agent=request.headers.get("user-agent")))
    db.commit()
    path = "app/static/resume/Nicholas_Spruce_Resume.pdf"
    return FileResponse(path, filename="Nicholas_Spruce_Resume.pdf", media_type="application/pdf")

# -------------------------------
# robots.txt
# -------------------------------
@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt(request: Request):
    return "\n".join([
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.url_for('sitemap_xml')}"
    ])

# -------------------------------
# sitemap
# -------------------------------
@app.get("/sitemap.xml", name="sitemap_xml")
def sitemap_xml(request: Request):
    # Always include your core pages
    urls = [
        str(request.url_for("home")),
        str(request.url_for("about")),
        str(request.url_for("projects")),
        str(request.url_for("contact_me")),
    ]

    for p in PROJECT_LIST:
        urls.append(str(request.url_for("project_detail", slug=p["slug"])))

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        *[f"  <url><loc>{u}</loc></url>" for u in urls],
        "</urlset>",
    ]
    return Response("\n".join(xml), media_type="application/xml")
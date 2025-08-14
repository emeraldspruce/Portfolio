# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .content_loader import load_json

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="app/templates")

HOME = load_json("home.json")
ABOUT = load_json("about.json")
PROJECTS = load_json("projects.json")
CONTACT_ME = load_json("contact_me.json")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "content": HOME
    })

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "content": ABOUT
    })

@app.get("/projects", response_class=HTMLResponse)
def projects(request: Request):
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "content": PROJECTS
    })

@app.get("/contact_me", response_class=HTMLResponse)
def contact_me(request: Request):
    return templates.TemplateResponse("contact_me.html", {
        "request": request,
        "content": CONTACT_ME
    })

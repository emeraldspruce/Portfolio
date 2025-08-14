import os
from typing import Optional, Sequence
from dotenv import load_dotenv
import httpx

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
MAIL_FROM = "emeraldspruce2005@gmail.com"
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Portfolio Site")
MAIL_TO = "emeraldspruce2005@gmail.com"
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

class EmailError(RuntimeError):
    pass

def _headers() -> dict:
    if not BREVO_API_KEY:
        raise EmailError("BREVO_API_KEY is not set.")
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY
    }

def _payload(
    subject: str,
    text: str,
    html: Optional[str],
    to: Optional[Sequence[str]],
    cc: Optional[Sequence[str]],
    bcc: Optional[Sequence[str]],
    reply_to: Optional[str],
) -> dict:
    recipients = [{"email": e} for e in (to or [MAIL_TO]) if e]
    if not MAIL_FROM or not recipients:
        raise EmailError("MAIL_FROM and at least one recipient must be set.")
    data = {
        "sender": {"name": MAIL_FROM_NAME, "email": MAIL_FROM},
        "to": recipients,
        "subject": subject,
        "textContent": text
    }
    if html:
        data["htmlContent"] = html
    if cc:
        data["cc"] = [{"email": e} for e in cc]
    if bcc:
        data["bcc"] = [{"email": e} for e in bcc]
    if reply_to:
        data["replyTo"] = {"email": reply_to}
    return data

def send_email(
    subject: str,
    text: str,
    html: Optional[str] = None,
    to: Optional[Sequence[str]] = None,
    cc: Optional[Sequence[str]] = None,
    bcc: Optional[Sequence[str]] = None,
    reply_to: Optional[str] = None,
    timeout: float = 10.0
) -> None:
    data = _payload(subject, text, html, to, cc, bcc, reply_to)
    with httpx.Client(timeout=timeout) as c:
        r = c.post(BREVO_URL, json=data, headers=_headers())
    if r.status_code >= 300:
        raise EmailError(f"Brevo error {r.status_code}: {r.text}")

async def send_email_async(
    subject: str,
    text: str,
    html: Optional[str] = None,
    to: Optional[Sequence[str]] = None,
    cc: Optional[Sequence[str]] = None,
    bcc: Optional[Sequence[str]] = None,
    reply_to: Optional[str] = None,
    timeout: float = 10.0
) -> None:
    data = _payload(subject, text, html, to, cc, bcc, reply_to)
    async with httpx.AsyncClient(timeout=timeout) as c:
        r = await c.post(BREVO_URL, json=data, headers=_headers())
    if r.status_code >= 300:
        raise EmailError(f"Brevo error {r.status_code}: {r.text}")

# Convenience functions for your contact form
def notify_new_contact(name: str, email: str, requested_transcript: bool, message: str) -> None:
    subject = f"New portfolio message from {name}"
    text = f"From: {name} <{email}>\nRequested transcript: {requested_transcript}\n\n{message}"
    send_email(subject=subject, text=text)

async def notify_new_contact_async(name: str, email: str, requested_transcript: bool, message: str) -> None:
    subject = f"New portfolio message from {name}"
    text = f"From: {name} <{email}>\nRequested transcript: {requested_transcript}\n\n{message}"
    await send_email_async(subject=subject, text=text)
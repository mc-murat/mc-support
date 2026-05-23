import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

import app.database as db
import app.analyzer as analyzer
import app.openai_client as openai_client
import app.auth as auth

app = FastAPI(title="mc-support")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "mc-support-dev-secret-change-in-prod"),
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR        = Path("uploads")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".log"}
MAX_FILE_BYTES     = 10 * 1024 * 1024  # 10 MB


@app.on_event("startup")
def startup():
    db.init_db()
    db.init_users([
        ("admin",   auth.hash_password("admin123"),   "admin"),
        ("support", auth.hash_password("support123"), "support"),
        ("user",    auth.hash_password("user123"),    "user"),
    ])
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Health (no auth) ────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "mc-support"}


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if auth.current_user(request):
        return RedirectResponse("/support", status_code=302)
    return Path("app/static/login.html").read_text(encoding="utf-8")


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(default="/support"),
):
    user = db.get_user(username)
    if not user or not auth.verify_password(password, user["password_hash"]):
        return RedirectResponse("/login?error=1", status_code=302)
    request.session["user"] = {"username": user["username"], "role": user["role"]}
    safe_next = next if next.startswith("/") and not next.startswith("//") else "/support"
    return RedirectResponse(safe_next, status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@app.get("/api/me")
def me(request: Request):
    user = auth.current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    return {"username": user["username"], "role": user["role"]}


# ── Support (alle eingeloggten Rollen) ──────────────────────────────────────

@app.get("/support", response_class=HTMLResponse)
def support_page(request: Request):
    if redirect := auth.require_login(request):
        return redirect
    return Path("app/static/support.html").read_text(encoding="utf-8")


@app.post("/submit")
async def submit_ticket(
    request: Request,
    user_name: str = Form(...),
    department: str = Form(...),
    message: str = Form(...),
    file: UploadFile | None = File(default=None),
):
    if redirect := auth.require_login(request):
        return redirect

    # ── File upload ──────────────────────────────────────────────────────────
    attachment_filename = ""
    attachment_path     = ""

    if file and file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return RedirectResponse("/support?error=upload_type", status_code=302)
        content = await file.read()
        if len(content) > MAX_FILE_BYTES:
            return RedirectResponse("/support?error=upload_size", status_code=302)
        unique_name = f"{uuid.uuid4().hex}{ext}"
        (UPLOAD_DIR / unique_name).write_bytes(content)
        attachment_filename = file.filename
        attachment_path     = unique_name

    # ── Ticket analysis ──────────────────────────────────────────────────────
    ai_result = openai_client.analyze(user_name, department, message)
    if ai_result:
        local     = analyzer.analyze(message)
        category  = ai_result["category"]
        priority  = ai_result["priority"]
        team      = ai_result["team"]
        summary   = ai_result["summary"]
        recommended_action = ai_result["recommended_action"]
        keywords  = local["keywords"]
    else:
        result    = analyzer.analyze(message)
        category  = result["category"]
        priority  = result["priority"]
        team      = result["team"]
        recommended_action = result["recommended_action"]
        keywords  = result["keywords"]
        summary   = analyzer.summarize(user_name, department, message, category, priority, team)

    ticket_id = db.insert_ticket(
        user_name=user_name,
        department=department,
        message=message,
        keywords=keywords,
        category=category,
        priority=priority,
        team=team,
        summary=summary,
        recommended_action=recommended_action,
        attachment_filename=attachment_filename,
        attachment_path=attachment_path,
    )
    return RedirectResponse(url=f"/support?success=1&id={ticket_id}", status_code=303)


# ── File download (login required) ──────────────────────────────────────────

@app.get("/uploads/{filename}")
def download_upload(filename: str, request: Request):
    if redirect := auth.require_login(request):
        return redirect
    safe_name = Path(filename).name  # prevent path traversal
    file_path = UPLOAD_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    return FileResponse(file_path, filename=safe_name)


# ── Admin (nur support + admin Rolle) ───────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    if redirect := auth.require_roles(request, auth.ADMIN_ROLES):
        return redirect
    return Path("app/static/admin.html").read_text(encoding="utf-8")


@app.get("/api/tickets")
def get_tickets(request: Request):
    auth.api_require_roles(request, auth.ADMIN_ROLES)
    return db.get_all_tickets()


@app.get("/api/stats")
def get_stats(request: Request):
    auth.api_require_roles(request, auth.ADMIN_ROLES)
    return db.get_stats()


class StatusUpdate(BaseModel):
    status: str


@app.patch("/api/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, body: StatusUpdate, request: Request):
    auth.api_require_roles(request, auth.ADMIN_ROLES)
    try:
        db.update_status(ticket_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}

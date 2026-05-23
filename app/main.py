from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import app.database as db
import app.analyzer as analyzer

app = FastAPI(title="mc-support")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup():
    db.init_db()


@app.get("/support", response_class=HTMLResponse)
def support_page():
    return Path("app/static/support.html").read_text(encoding="utf-8")


@app.post("/submit")
def submit_ticket(
    user_name: str = Form(...),
    department: str = Form(...),
    message: str = Form(...),
):
    result = analyzer.analyze(message)
    summary = analyzer.summarize(
        user_name, department, message,
        result["category"], result["priority"], result["team"],
    )
    ticket_id = db.insert_ticket(
        user_name=user_name,
        department=department,
        message=message,
        keywords=result["keywords"],
        category=result["category"],
        priority=result["priority"],
        team=result["team"],
        summary=summary,
        recommended_action=result["recommended_action"],
    )
    return RedirectResponse(url=f"/support?success=1&id={ticket_id}", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return Path("app/static/admin.html").read_text(encoding="utf-8")


@app.get("/api/tickets")
def get_tickets():
    return db.get_all_tickets()


@app.get("/api/stats")
def get_stats():
    return db.get_stats()


class StatusUpdate(BaseModel):
    status: str


@app.patch("/api/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, body: StatusUpdate):
    try:
        db.update_status(ticket_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}

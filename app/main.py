from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import app.database as db
import app.analyzer as analyzer
import app.openai_client as openai_client

app = FastAPI(title="mc-support")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup():
    db.init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "mc-support"}


@app.get("/support", response_class=HTMLResponse)
def support_page():
    return Path("app/static/support.html").read_text(encoding="utf-8")


@app.post("/submit")
def submit_ticket(
    user_name: str = Form(...),
    department: str = Form(...),
    message: str = Form(...),
):
    ai_result = openai_client.analyze(user_name, department, message)
    if ai_result:
        local = analyzer.analyze(message)
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

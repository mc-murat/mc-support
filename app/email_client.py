import logging
import os
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def _configured() -> bool:
    return all(os.environ.get(k) for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"))


def _send(to: str, subject: str, body: str) -> None:
    if not to:
        return
    if not _configured():
        logger.info("SMTP nicht konfiguriert — E-Mail an %s wird übersprungen (%s)", to, subject)
        return

    host  = os.environ["SMTP_HOST"]
    port  = int(os.environ.get("SMTP_PORT", "587"))
    user  = os.environ["SMTP_USER"]
    pw    = os.environ["SMTP_PASSWORD"]
    from_ = os.environ["SMTP_FROM"]

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = from_
    msg["To"]      = to

    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(user, pw)
            smtp.sendmail(from_, [to], msg.as_string())
        logger.info("E-Mail gesendet an %s: %s", to, subject)
    except Exception as exc:
        logger.warning("E-Mail Versand fehlgeschlagen: %s", exc)


def send_ticket_created(
    to: str,
    ticket_id: int,
    category: str,
    priority: str,
    status: str,
    summary: str,
) -> None:
    subject = f"[MC-SUPPORT] Ticket #{ticket_id} erstellt"
    body = (
        f"Dein Support-Ticket wurde erfolgreich erstellt.\n\n"
        f"Ticket-ID:       #{ticket_id}\n"
        f"Kategorie:       {category}\n"
        f"Priorität:       {priority}\n"
        f"Status:          {status}\n"
        f"Zusammenfassung: {summary}\n\n"
        f"Die IT-Abteilung kümmert sich um dein Anliegen.\n"
        f"Bitte halte die Ticket-ID für Rückfragen bereit."
    )
    _send(to, subject, body)


def send_status_changed(
    to: str,
    ticket_id: int,
    new_status: str,
    team: str,
) -> None:
    subject = f"[MC-SUPPORT] Ticket #{ticket_id} — Status aktualisiert"
    body = (
        f"Der Status deines Support-Tickets wurde aktualisiert.\n\n"
        f"Ticket-ID:    #{ticket_id}\n"
        f"Neuer Status: {new_status}\n"
        f"Team:         {team}\n\n"
        f"Bei Fragen wende dich an den IT-Support."
    )
    _send(to, subject, body)

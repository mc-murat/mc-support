import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path("tickets.db")

VALID_STATUSES = {"Neu", "Offen", "In Bearbeitung", "Geschlossen"}


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _add_column(conn, column: str, definition: str):
    try:
        conn.execute(f"ALTER TABLE tickets ADD COLUMN {column} {definition}")
    except Exception:
        pass  # column already exists


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name          TEXT NOT NULL DEFAULT '',
            department         TEXT NOT NULL DEFAULT '',
            message            TEXT NOT NULL,
            keywords           TEXT NOT NULL DEFAULT '',
            category           TEXT NOT NULL,
            priority           TEXT NOT NULL,
            team               TEXT NOT NULL,
            summary            TEXT NOT NULL DEFAULT '',
            recommended_action TEXT NOT NULL DEFAULT '',
            status             TEXT NOT NULL DEFAULT 'Neu',
            created_at         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
        )
    """)
    # Migrations for databases created with the old schema
    _add_column(conn, "user_name",          "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "department",         "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "keywords",           "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "recommended_action", "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "created_at",         "TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))")
    conn.commit()
    conn.close()


def insert_ticket(
    user_name: str,
    department: str,
    message: str,
    keywords: list[str],
    category: str,
    priority: str,
    team: str,
    summary: str,
    recommended_action: str,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO tickets
           (user_name, department, message, keywords, category, priority,
            team, summary, recommended_action, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Neu')""",
        (
            user_name, department, message,
            ", ".join(keywords),
            category, priority, team,
            summary, recommended_action,
        ),
    )
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def update_status(ticket_id: int, new_status: str):
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Ungültiger Status: {new_status}")
    conn = get_connection()
    conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()


def get_all_tickets() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats() -> dict:
    today = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    open_count = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status != 'Geschlossen'"
    ).fetchone()[0]
    high_count = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE priority = 'Hoch'"
    ).fetchone()[0]
    today_count = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()[0]
    conn.close()
    return {"open": open_count, "high_priority": high_count, "today": today_count}

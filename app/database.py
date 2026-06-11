import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path("data/tickets.db")

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


def init_users(default_users: list[tuple[str, str, str]]):
    """Create users table and seed default accounts (username, password_hash, role)."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'user'
        )
    """)
    for username, password_hash, role in default_users:
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
    conn.commit()
    conn.close()


def get_user(username: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
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
    _add_column(conn, "user_name",            "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "department",           "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "keywords",             "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "recommended_action",   "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "created_at",           "TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))")
    _add_column(conn, "attachment_filename",  "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "attachment_path",      "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "solution_steps",       "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "email",                "TEXT NOT NULL DEFAULT ''")
    conn.commit()
    conn.close()


def get_ticket(ticket_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


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
    attachment_filename: str = "",
    attachment_path: str = "",
    solution_steps: str = "",
    email: str = "",
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO tickets
           (user_name, department, message, keywords, category, priority,
            team, summary, recommended_action, status,
            attachment_filename, attachment_path, solution_steps, email)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Neu', ?, ?, ?, ?)""",
        (
            user_name, department, message,
            ", ".join(keywords),
            category, priority, team,
            summary, recommended_action,
            attachment_filename, attachment_path,
            solution_steps, email,
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


def get_analytics() -> dict:
    conn = get_connection()

    def group_by(col: str) -> list[dict]:
        rows = conn.execute(
            f"SELECT {col}, COUNT(*) as count FROM tickets GROUP BY {col} ORDER BY count DESC"
        ).fetchall()
        return [{"label": r[0] or "–", "count": r[1]} for r in rows]

    by_day_rows = conn.execute(
        """SELECT DATE(created_at) as day, COUNT(*) as count
           FROM tickets
           WHERE created_at >= DATE('now', '-13 days')
           GROUP BY day
           ORDER BY day"""
    ).fetchall()
    by_day = [{"label": r[0], "count": r[1]} for r in by_day_rows]

    total    = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    closed   = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Geschlossen'").fetchone()[0]
    high     = conn.execute("SELECT COUNT(*) FROM tickets WHERE priority = 'Hoch'").fetchone()[0]
    top_cat  = conn.execute("SELECT category FROM tickets GROUP BY category ORDER BY COUNT(*) DESC LIMIT 1").fetchone()
    top_team = conn.execute("SELECT team     FROM tickets GROUP BY team     ORDER BY COUNT(*) DESC LIMIT 1").fetchone()

    result = {
        "summary": {
            "total":         total,
            "closed":        closed,
            "high_priority": high,
            "top_category":  top_cat[0]  if top_cat  else None,
            "top_team":      top_team[0] if top_team else None,
        },
        "by_category": group_by("category"),
        "by_priority": group_by("priority"),
        "by_status":   group_by("status"),
        "by_team":     group_by("team"),
        "by_day":      by_day,
    }
    conn.close()
    return result


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

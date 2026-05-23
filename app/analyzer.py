KEYWORD_RULES = [
    # (keyword, category, priority, team, recommended_action)
    ("vpn",      "Netzwerk / VPN",  "Hoch",    "Netzwerk-Team",  "VPN-Client neu starten, Zugangsdaten prüfen oder Netzwerk-Team kontaktieren."),
    ("outlook",  "Mail / Software", "Mittel",  "Workplace-Team", "Outlook-Profil neu einrichten oder Mailbox-Synchronisation erzwingen."),
    ("passwort", "Account",         "Hoch",    "IAM-Team",       "Passwort über Self-Service-Portal zurücksetzen oder IAM-Team kontaktieren."),
    ("password", "Account",         "Hoch",    "IAM-Team",       "Passwort über Self-Service-Portal zurücksetzen oder IAM-Team kontaktieren."),
    ("drucker",  "Hardware",        "Mittel",  "Support-Team",   "Druckertreiber neu installieren oder Drucker neu starten."),
    ("teams",    "Software",        "Niedrig", "Workplace-Team", "Teams-Cache leeren (AppData\\Roaming\\Microsoft\\Teams) oder App neu installieren."),
]

PRIORITY_RANK = {"Hoch": 3, "Mittel": 2, "Niedrig": 1}

_DEFAULT_ACTION = "Problembeschreibung prüfen und Ticket manuell kategorisieren."


def analyze(message: str) -> dict:
    text = message.lower()
    seen_keywords: set[str] = set()
    matched = []

    for keyword, category, priority, team, action in KEYWORD_RULES:
        if keyword in text and keyword not in seen_keywords:
            seen_keywords.add(keyword)
            matched.append({
                "keyword": keyword,
                "category": category,
                "priority": priority,
                "team": team,
                "recommended_action": action,
            })

    if not matched:
        return {
            "keywords": [],
            "category": "Allgemein",
            "priority": "Niedrig",
            "team": "Support-Team",
            "recommended_action": _DEFAULT_ACTION,
        }

    # If multiple keywords matched, use the highest-priority entry
    best = max(matched, key=lambda m: PRIORITY_RANK[m["priority"]])
    return {
        "keywords": [m["keyword"] for m in matched],
        "category": best["category"],
        "priority": best["priority"],
        "team": best["team"],
        "recommended_action": best["recommended_action"],
    }


def summarize(
    user_name: str, department: str, message: str,
    category: str, priority: str, team: str,
) -> str:
    short = message[:120] + ("…" if len(message) > 120 else "")
    dept = f" ({department})" if department else ""
    return (
        f"Ticket von {user_name}{dept} – Bereich: {category}, "
        f"Priorität: {priority}, Zuständig: {team}. Meldung: {short}"
    )

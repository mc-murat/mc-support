import json
import os

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


_SYSTEM_PROMPT = """Du bist ein IT-Support-Assistent. Analysiere die folgende Support-Anfrage und antworte ausschließlich mit einem JSON-Objekt (kein Markdown, kein Text davor oder danach) mit diesen Feldern:

- category: Kurze Kategorie auf Deutsch (z.B. "Account", "Netzwerk / VPN", "Hardware", "Software", "Mail / Software", "Allgemein")
- priority: Genau eines von "Hoch", "Mittel" oder "Niedrig"
- team: Zuständiges Team (z.B. "IAM-Team", "Netzwerk-Team", "Workplace-Team", "Support-Team")
- summary: Ein Satz, der das Problem zusammenfasst
- recommended_action: Konkrete Handlungsempfehlung für den IT-Support"""

_REQUIRED_KEYS = {"category", "priority", "team", "summary", "recommended_action"}
_VALID_PRIORITIES = {"Hoch", "Mittel", "Niedrig"}


def analyze(user_name: str, department: str, message: str) -> dict | None:
    """Call OpenAI to analyze a support ticket. Returns None if unavailable or on error."""
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    try:
        client = _get_client()
        user_content = f"Benutzer: {user_name}\nAbteilung: {department}\nProblem: {message}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)

        if not _REQUIRED_KEYS.issubset(data.keys()):
            return None
        if data["priority"] not in _VALID_PRIORITIES:
            return None

        return data

    except Exception:
        return None

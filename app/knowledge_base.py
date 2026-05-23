_KB: dict[str, dict] = {
    "vpn": {
        "cause": "VPN-Client nicht verbunden, falsche Konfiguration oder Zertifikat abgelaufen.",
        "steps": [
            "VPN-Client öffnen und Verbindungsstatus prüfen.",
            "Verbindung trennen und neu aufbauen.",
            "Netzwerkverbindung (WLAN/LAN) prüfen — VPN benötigt aktives Internet.",
            "VPN-Konfigurationsprofil löschen und neu importieren.",
            "Systemzeit prüfen — abweichende Uhrzeit kann Zertifikatsfehler verursachen.",
            "IT-Support kontaktieren, falls Zertifikat abgelaufen ist.",
        ],
        "action": "VPN-Client neu starten und erneut verbinden. Falls das Problem bleibt, VPN-Profil neu importieren.",
    },
    "outlook": {
        "cause": "Outlook-Profil beschädigt, falsches Passwort oder Postfach-Synchronisierung unterbrochen.",
        "steps": [
            "Outlook schliessen und neu starten.",
            "Internetverbindung prüfen.",
            "Passwort prüfen: Anmeldedaten in Windows-Anmeldeinformationsverwaltung aktualisieren.",
            "Posteingang manuell synchronisieren (F9 oder Senden/Empfangen).",
            "Outlook im abgesicherten Modus starten: outlook.exe /safe",
            "Outlook-Profil reparieren: Systemsteuerung → Mail → Profile anzeigen → Reparieren.",
        ],
        "action": "Outlook neu starten und manuell synchronisieren (F9). Bei Passwortproblem: Anmeldeinformationen in Windows aktualisieren.",
    },
    "passwort": {
        "cause": "Passwort abgelaufen, gesperrt nach zu vielen Fehlversuchen oder vergessen.",
        "steps": [
            "Prüfen, ob Konto gesperrt ist (Fehlermeldung lesen).",
            "Passwort-Reset-Link (Self-Service-Portal) aufrufen, falls verfügbar.",
            "IT-Support kontaktieren für manuelle Entsperrung.",
            "Neues Passwort gemäss Passwortrichtlinie wählen (mind. 12 Zeichen, Sonderzeichen).",
            "Gespeicherte Passwörter in Browser und Apps aktualisieren.",
        ],
        "action": "Self-Service-Passwort-Reset verwenden. Falls nicht möglich, IT-Support für Entsperrung kontaktieren.",
    },
    "drucker": {
        "cause": "Drucker offline, Treiberfehler, Verbindungsproblem oder Papierstau.",
        "steps": [
            "Druckerstatus prüfen: Einstellungen → Drucker und Scanner.",
            "Drucker aus- und einschalten.",
            "Druckerwarteschlange leeren: alle ausstehenden Aufträge löschen.",
            "Druckertreiber neu installieren.",
            "Netzwerkverbindung des Druckers prüfen (Ping auf Drucker-IP).",
            "Drucker aus Windows entfernen und neu hinzufügen.",
        ],
        "action": "Druckerwarteschlange leeren und Drucker neu starten. Falls offline: Drucker aus Windows entfernen und neu hinzufügen.",
    },
    "teams": {
        "cause": "Teams-Cache beschädigt, Anmeldefehler oder Netzwerkproblem.",
        "steps": [
            "Teams vollständig schliessen (auch Systemtray).",
            "Teams-Cache löschen: %appdata%\\Microsoft\\Teams\\Cache leeren.",
            "Teams neu starten und neu anmelden.",
            "Windows-Anmeldeinformationen für Teams prüfen.",
            "Teams-Desktop-App deinstallieren und neu installieren.",
            "Netzwerkverbindung prüfen — Teams benötigt UDP-Ports 3478–3481.",
        ],
        "action": "Teams schliessen, Cache unter %appdata%\\Microsoft\\Teams\\Cache leeren und neu starten.",
    },
}

_FALLBACK = {
    "cause": "Technisches Problem — genaue Ursache noch unbekannt.",
    "steps": [
        "Gerät neu starten.",
        "Internetverbindung prüfen.",
        "Betroffene Anwendung schliessen und neu starten.",
        "Fehlermeldung notieren und an IT-Support weitergeben.",
        "IT-Support kontaktieren mit genauer Beschreibung des Problems.",
    ],
    "action": "Gerät neu starten und prüfen, ob das Problem weiterhin besteht. Fehlermeldung für den Support notieren.",
}

_KEYWORD_MAP = {
    "vpn":      "vpn",
    "cisco":    "vpn",
    "tunnel":   "vpn",
    "outlook":  "outlook",
    "mail":     "outlook",
    "e-mail":   "outlook",
    "email":    "outlook",
    "postfach": "outlook",
    "passwort": "passwort",
    "password": "passwort",
    "gesperrt": "passwort",
    "login":    "passwort",
    "anmelden": "passwort",
    "drucker":  "drucker",
    "drucken":  "drucker",
    "druckerwarteschlange": "drucker",
    "teams":    "teams",
    "meeting":  "teams",
    "besprechung": "teams",
}


def get_solution(keywords: list[str]) -> str:
    import json
    template = _FALLBACK
    for kw in keywords:
        key = _KEYWORD_MAP.get(kw.lower())
        if key and key in _KB:
            template = _KB[key]
            break
    return json.dumps({
        "cause":  template["cause"],
        "steps":  template["steps"],
        "action": template["action"],
    }, ensure_ascii=False)

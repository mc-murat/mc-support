# mc-support

Internes IT-Support-Ticketsystem für Mitarbeitende. Entwickelt im Rahmen von Modul 300.

## Login – Test-Zugangsdaten

| Benutzer  | Passwort     | Rolle     | Zugriff              |
|-----------|--------------|-----------|----------------------|
| `admin`   | `admin123`   | admin     | /support + /admin    |
| `support` | `support123` | support   | /support + /admin    |
| `user`    | `user123`    | user      | nur /support         |

Nicht eingeloggte Benutzer werden automatisch zu `/login` weitergeleitet.

## Features

- Supportformular für Mitarbeitende (`/support`)
- Admin-Dashboard für IT-Support (`/admin`)
- Automatische Ticket-Analyse (lokal per Keyword oder optional via OpenAI)
- Status-Verwaltung direkt im Admin-Dashboard
- Datenpersistenz mit SQLite
- Healthcheck-Endpoint (`/health`)
- Docker-fähig

## Lokale Installation (ohne Docker)

```bash
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

## Start mit Docker

```bash
docker compose up -d
```

## Stoppen

```bash
docker compose down
```

## Logs anzeigen

```bash
# Live verfolgen
docker compose logs -f

# Nur die letzten 50 Zeilen
docker compose logs --tail 50
```

## Neu bauen (nach Code-Änderungen)

```bash
docker compose up -d --build
```

## OpenAI API Key (optional)

Ohne API Key läuft die App weiterhin mit lokaler Keyword-Analyse.

```bash
# .env aus der Vorlage erstellen
cp .env.example .env
```

`.env` öffnen und Key eintragen:

```
OPENAI_API_KEY=sk-...
```

Danach Container neu bauen:

```bash
docker compose up -d --build
```

## Wichtige URLs

| Seite            | URL                          |
|------------------|------------------------------|
| Supportformular  | http://localhost:8000/support |
| Admin-Dashboard  | http://localhost:8000/admin   |
| Healthcheck      | http://localhost:8000/health  |

## File Upload

Mitarbeitende können optional einen Anhang zum Ticket hochladen (z. B. Screenshot, Logdatei).

**Erlaubte Dateitypen:** PNG, JPG, JPEG, PDF, TXT, LOG  
**Maximale Dateigrösse:** 10 MB

Hochgeladene Dateien werden im Ordner `uploads/` gespeichert und bleiben nach Container-Neustarts erhalten.  
Der Download-Link ist im Admin-Dashboard in den Ticket-Details sichtbar (nur für eingeloggte Benutzer).

## Datenspeicherung

Die SQLite-Datenbank liegt unter `data/tickets.db` und wird ausserhalb des Containers gespeichert.
Bei `docker compose down` bleiben alle Tickets erhalten.

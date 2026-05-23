# mc-support

Internes IT-Support-Ticketsystem mit FastAPI und SQLite.

## Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert und gestartet

## Start mit Docker

```bash
docker compose up -d
```

Die App ist danach erreichbar unter:

| Seite | URL |
|---|---|
| Supportformular | http://localhost:8000/support |
| Admin-Dashboard | http://localhost:8000/admin |

## Stop

```bash
docker compose down
```

## Logs anzeigen

```bash
# Logs live verfolgen
docker compose logs -f

# Nur die letzten 50 Zeilen
docker compose logs --tail 50
```

## Neu bauen (nach Code-Änderungen)

```bash
docker compose up -d --build
```

## Lokale Entwicklung (ohne Docker)

```bash
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

## OpenAI API Key (optional)

Die App kann Tickets mit OpenAI analysieren. Ohne API Key wird automatisch die lokale Analyse verwendet – die App läuft in beiden Fällen fehlerfrei.

```bash
# .env aus der Vorlage erstellen
cp .env.example .env
```

Dann `.env` öffnen und den Key eintragen:

```
OPENAI_API_KEY=sk-...
```

Danach Container neu starten:

```bash
docker compose up -d --build
```

**Ohne API Key:** Die lokale Keyword-Analyse übernimmt automatisch Kategorie, Priorität und Team.

## Datenspeicherung

Die SQLite-Datenbank liegt unter `data/tickets.db` und wird ausserhalb des Containers gespeichert.  
Bei `docker compose down` bleiben alle Tickets erhalten.

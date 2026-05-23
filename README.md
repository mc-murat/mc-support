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

## Datenspeicherung

Die SQLite-Datenbank liegt unter `data/tickets.db` und wird ausserhalb des Containers gespeichert.  
Bei `docker compose down` bleiben alle Tickets erhalten.

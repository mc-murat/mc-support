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
- **Knowledge Base**: lokale Lösungsvorschläge für VPN, Outlook, Passwort, Drucker, Teams
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

## E-Mail Benachrichtigungen (optional)

Ohne SMTP-Konfiguration läuft die App weiterhin fehlerfrei — E-Mails werden dann nur geloggt und nicht gesendet.

```bash
cp .env.example .env
```

`.env` öffnen und SMTP-Daten eintragen:

```
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=dein-user
SMTP_PASSWORD=dein-passwort
SMTP_FROM=mc-support@firma.ch
```

**Empfohlene Testdienste:**

| Dienst   | Beschreibung                                                      |
|----------|-------------------------------------------------------------------|
| [Mailtrap](https://mailtrap.io) | Sandboxed SMTP für Entwicklung — E-Mails landen in einer Inbox, nicht beim Empfänger |
| Gmail    | SMTP über `smtp.gmail.com:587` mit App-Passwort (2FA aktivieren) |

**Wann werden E-Mails gesendet:**
- Bei Ticketerstellung: Ticket-ID, Kategorie, Priorität, Status, Zusammenfassung
- Bei Statusänderung: neuer Status, Ticket-ID, zuständiges Team

Das E-Mail-Feld im Supportformular ist optional. Ohne Angabe werden keine E-Mails gesendet.

Danach Container neu bauen:

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

## Analytics Dashboard

Das Analytics Dashboard ist **ausschliesslich für die Rolle `admin`** sichtbar. Support-Benutzer sehen die Ticketliste, aber keinen Analytics-Bereich. Der Endpoint `GET /api/analytics` gibt bei Support-Rolle `403 Forbidden` zurück.

**Kennzahlen (KPI-Leiste):**

| KPI                  | Beschreibung                                              |
|----------------------|-----------------------------------------------------------|
| Gesamt               | Gesamtanzahl aller Tickets                                |
| Abschlussquote       | Anteil geschlossener Tickets in %                         |
| Hohe Priorität       | Anteil Tickets mit Priorität "Hoch" in %                  |
| Top Kategorie        | Häufigste Problemkategorie                                |
| Top Team             | Meistbelastetes Support-Team                              |

**Charts (Chart.js via CDN):**

| Diagramm                        | Typ                  | Beschreibung                                   |
|---------------------------------|----------------------|------------------------------------------------|
| Tickets nach Status             | Donut Chart          | Neu / Offen / In Bearbeitung / Geschlossen     |
| Tickets nach Priorität          | Donut Chart          | Hoch / Mittel / Niedrig                        |
| Tickets nach Kategorie          | Horizontaler Balken  | Häufigste Problemkategorien                    |
| Auslastung pro Team             | Horizontaler Balken  | Ticket-Volumen je Support-Team                 |
| Ticket-Aufkommen (14 Tage)      | Liniendiagramm       | Täglicher Eingang der letzten zwei Wochen      |

Daten werden direkt aus SQLite berechnet (`GET /api/analytics`). Kein Backend-Service nötig.

## Knowledge Base

Für jedes Ticket werden automatisch Lösungsschritte generiert, basierend auf den erkannten Keywords.

**Lokale Vorlagen (immer verfügbar):**

| Kategorie | Keywords |
|-----------|----------|
| VPN       | vpn, cisco, tunnel |
| Outlook   | outlook, mail, e-mail, postfach |
| Passwort  | passwort, password, gesperrt, login |
| Drucker   | drucker, drucken |
| Teams     | teams, meeting, besprechung |
| Allgemein | (Fallback für alle anderen Fälle) |

Jede Vorlage enthält mögliche Ursache, konkrete Prüfschritte und eine empfohlene Erstaktion.  
Falls OpenAI aktiviert ist, werden die Lösungsschritte durch die KI optimiert.

Die Lösungsvorschläge sind nur im Admin-Dashboard sichtbar (nicht im Supportformular).

## File Upload

Mitarbeitende können optional einen Anhang zum Ticket hochladen (z. B. Screenshot, Logdatei).

**Erlaubte Dateitypen:** PNG, JPG, JPEG, PDF, TXT, LOG  
**Maximale Dateigrösse:** 10 MB

Hochgeladene Dateien werden im Ordner `uploads/` gespeichert und bleiben nach Container-Neustarts erhalten.  
Der Download-Link ist im Admin-Dashboard in den Ticket-Details sichtbar (nur für eingeloggte Benutzer).

## Datenspeicherung

Die SQLite-Datenbank liegt unter `data/tickets.db` und wird ausserhalb des Containers gespeichert.
Bei `docker compose down` bleiben alle Tickets erhalten.

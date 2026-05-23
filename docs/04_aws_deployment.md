# AWS Deployment – mc-support

## Ziel

Die mc-support Applikation auf einer AWS EC2-Instanz mit Docker betreiben.

---

## Voraussetzungen

- AWS-Konto vorhanden
- SSH-Schlüsselpaar erstellt
- Repository auf GitHub vorhanden
- OpenAI API Key (optional)

---

## EC2 Instanz erstellen

1. AWS Management Console öffnen → **EC2** → **Launch Instance**
2. Name: `mc-support`
3. AMI: **Ubuntu Server 24.04 LTS**
4. Instance Type: `t2.micro` (Free Tier)
5. Key Pair: vorhandenes Schlüsselpaar auswählen oder neues erstellen
6. Unter **Network Settings**: Security Group konfigurieren (siehe nächster Abschnitt)
7. **Launch Instance** klicken

---

## Security Group konfigurieren

Folgende Inbound Rules setzen:

| Typ        | Port | Quelle    | Zweck              |
|------------|------|-----------|--------------------|
| SSH        | 22   | Meine IP  | SSH-Zugriff        |
| Custom TCP | 8000 | 0.0.0.0/0 | FastAPI Applikation |

---

## Per SSH verbinden

```bash
ssh -i <dein-schluessel.pem> ubuntu@<öffentliche-IP>
```

---

## Docker installieren

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
newgrp docker
```

Installation prüfen:

```bash
docker --version
docker compose version
```

---

## Repository klonen

```bash
git clone https://github.com/<dein-username>/mc-support.git
cd mc-support
```

---

## .env Datei erstellen

```bash
cp .env.example .env
nano .env
```

`OPENAI_API_KEY` eintragen (oder leer lassen für lokale Analyse):

```
OPENAI_API_KEY=sk-...
```

---

## Anwendung starten

```bash
docker compose up -d --build
```

---

## Anwendung testen

Im Browser oder per curl:

```bash
curl http://<öffentliche-IP>:8000/health
```

Erwartete Antwort:

```json
{"status": "ok", "service": "mc-support"}
```

Vollständige URLs:

| Seite           | URL                                    |
|-----------------|----------------------------------------|
| Supportformular | http://\<öffentliche-IP\>:8000/support |
| Admin-Dashboard | http://\<öffentliche-IP\>:8000/admin   |
| Healthcheck     | http://\<öffentliche-IP\>:8000/health  |

---

## Logs prüfen

```bash
# Live verfolgen
docker compose logs -f

# Nur die letzten 50 Zeilen
docker compose logs --tail 50
```

---

## Container stoppen

```bash
docker compose down
```

Die SQLite-Datenbank bleibt unter `data/tickets.db` erhalten.

# AWS Deployment – mc-support

## Ziel

Die mc-support Applikation auf einer AWS EC2-Instanz mit Docker betreiben.

---

## Option A: Terraform (empfohlen)

Infrastruktur automatisch bereitstellen mit der Konfiguration im Ordner `terraform/`.

### Voraussetzungen

- [Terraform](https://developer.hashicorp.com/terraform/downloads) ≥ 1.3 installiert
- AWS CLI konfiguriert (`aws configure`) oder AWS Learner Lab Credentials gesetzt
- SSH Key Pair in AWS vorhanden

### Konfiguration

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` anpassen:

```hcl
aws_region       = "us-east-1"
instance_type    = "t3.micro"
key_pair_name    = "mein-schluessel"       # Name des Key Pairs in AWS
allowed_ssh_cidr = "203.0.113.10/32"       # Eigene öffentliche IP (curl ifconfig.me)
environment      = "dev"
```

> **AWS Learner Lab:** Region auf `us-east-1` belassen. Credentials aus dem Lab-Portal kopieren und als Umgebungsvariablen setzen:
> ```bash
> export AWS_ACCESS_KEY_ID=...
> export AWS_SECRET_ACCESS_KEY=...
> export AWS_SESSION_TOKEN=...
> ```

### Infrastruktur erstellen

```bash
terraform init
terraform plan
terraform apply
```

Nach `apply` werden die Outputs angezeigt:

```
public_ip   = "54.123.45.67"
app_url     = "http://54.123.45.67:8000"
ssh_command = "ssh -i <dein-schluessel.pem> ubuntu@54.123.45.67"
```

Die angezeigte IP ist eine **Elastic IP** — sie bleibt bei Instanz-Neustarts stabil und kann später einem DNS-Eintrag (z. B. über Route 53) zugewiesen werden.

> **Hinweis:** Eine nicht mit einer laufenden Instanz verknüpfte Elastic IP verursacht bei AWS Kosten. Immer `terraform destroy` ausführen, wenn die Infrastruktur nicht mehr benötigt wird — das gibt die EIP automatisch frei.

### Infrastruktur löschen

```bash
terraform destroy
```

Dieser Befehl löscht EC2 Instanz **und** Elastic IP vollständig.

---

## Option B: Manuell über AWS Console

### Voraussetzungen

- AWS-Konto vorhanden
- SSH-Schlüsselpaar erstellt
- Repository auf GitHub vorhanden
- OpenAI API Key (optional)

---

## EC2 Instanz erstellen (manuell)

1. AWS Management Console öffnen → **EC2** → **Launch Instance**
2. Name: `mc-support`
3. AMI: **Ubuntu Server 22.04 LTS**
4. Instance Type: `t3.micro`
5. Key Pair: vorhandenes Schlüsselpaar auswählen oder neues erstellen
6. Unter **Network Settings**: Security Group konfigurieren (siehe nächster Abschnitt)
7. **Launch Instance** klicken

---

## Security Group konfigurieren (manuell)

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

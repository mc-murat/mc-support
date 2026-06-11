# Terraform Deployment

## Ziel

Deployment der mc-support Anwendung auf AWS EC2 mit Terraform.

---

## Verwendete Technologien

* Terraform
* AWS EC2
* AWS Security Groups
* Elastic IP
* Ubuntu Server
* Docker Deployment

---

## Terraform Initialisierung

```powershell
terraform init
```

Ergebnis:

* AWS Provider heruntergeladen
* .terraform.lock.hcl erstellt

---

## AWS Credentials setzen

AWS Learner Lab Credentials wurden als Umgebungsvariablen gesetzt:

```powershell
$env:AWS_ACCESS_KEY_ID="..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_SESSION_TOKEN="..."
$env:AWS_DEFAULT_REGION="us-east-1"
```

---

## Terraform Plan

```powershell
terraform plan
```

Verwendete Werte:

* allowed_ssh_cidr = eigene öffentliche IP /32
* key_pair_name = m300-key

Terraform plante:

* EC2 Instanz
* Security Group

---

## Terraform Apply

```powershell
terraform apply
```

Erstellte Ressourcen:

* aws_instance.mc_support
* aws_security_group.mc_support

Outputs:

* public_ip
* app_url
* ssh_command

---

## Elastic IP

Später wurde zusätzlich eine Elastic IP erstellt:

```powershell
terraform apply
```

Neue Ressource:

* aws_eip.mc_support

Neue feste IP:

* 100.51.95.35

---

## Security Group

Erlaubte Ports:

* 22/tcp → nur eigene IP
* 8000/tcp → öffentlich

---

## SSH Verbindung

Verbindung zur EC2 Instanz erfolgreich:

```powershell
ssh -i m300-key.pem ubuntu@100.51.95.35
```

---

## Erkenntnisse

Terraform ermöglicht:

* Infrastructure as Code
* reproduzierbare Deployments
* saubere Cloud-Ressourcen
* einfaches Löschen mit terraform destroy

```
```

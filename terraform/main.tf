terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3"
}

provider "aws" {
  region = var.aws_region
}

# ── Security Group ────────────────────────────────────────────────────────────

resource "aws_security_group" "mc_support" {
  name        = "mc-support-sg"
  description = "mc-support: SSH + App Port 8000"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "App"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "mc-support-sg"
    Project     = "mc-support"
    Environment = var.environment
  }
}

# ── EC2 Instance ──────────────────────────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "mc_support" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.mc_support.id]

  tags = {
    Name        = "mc-support"
    Project     = "mc-support"
    Environment = var.environment
  }
}

# ── Elastic IP ────────────────────────────────────────────────────────────────

resource "aws_eip" "mc_support" {
  instance = aws_instance.mc_support.id
  domain   = "vpc"

  tags = {
    Name        = "mc-support-eip"
    Project     = "mc-support"
    Environment = var.environment
  }
}

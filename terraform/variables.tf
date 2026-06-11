variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 Instance Type"
  type        = string
  default     = "t3.micro"
}

variable "key_pair_name" {
  description = "Name des AWS Key Pairs für SSH-Zugriff"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR-Block für SSH-Zugriff (z. B. deine öffentliche IP: 203.0.113.10/32)"
  type        = string
}

variable "environment" {
  description = "Umgebungsbezeichnung für Tags"
  type        = string
  default     = "dev"
}

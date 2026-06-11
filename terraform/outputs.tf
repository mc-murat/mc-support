output "public_ip" {
  description = "Elastic IP der EC2 Instanz (stabil, bleibt bei Neustart erhalten)"
  value       = aws_eip.mc_support.public_ip
}

output "app_url" {
  description = "URL der mc-support Anwendung"
  value       = "http://${aws_eip.mc_support.public_ip}:8000"
}

output "ssh_command" {
  description = "SSH-Befehl zum Verbinden"
  value       = "ssh -i <dein-schluessel.pem> ubuntu@${aws_eip.mc_support.public_ip}"
}

output "alb_dns_name" {
  description = "DNS del Application Load Balancer."
  value       = aws_lb.app.dns_name
}

output "app_url" {
  description = "URL pública de la aplicación (si Route53 está configurado)."
  value       = var.route53_zone_id == "" ? null : "https://${local.app_domain}"
}

output "cdn_url" {
  description = "URL pública del CDN de imágenes."
  value       = local.cdn_public_url
}

output "rds_endpoint" {
  description = "Endpoint de RDS (privado)."
  value       = aws_db_instance.postgres.address
}

output "images_bucket" {
  value = aws_s3_bucket.images.bucket
}

output "db_secret_arn" {
  value = aws_secretsmanager_secret.db.arn
}

output "jwt_secret_arn" {
  value = aws_secretsmanager_secret.jwt.arn
}

output "ecr_backend_repo" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_repo" {
  value = aws_ecr_repository.frontend.repository_url
}

output "ecs_cluster" {
  value = aws_ecs_cluster.main.name
}

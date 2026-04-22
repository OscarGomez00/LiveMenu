variable "project" {
  description = "Nombre del proyecto (se usa como prefijo de recursos)."
  type        = string
  default     = "livemenu"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)."
  type        = string
  default     = "prod"
}

variable "region" {
  description = "Región AWS principal."
  type        = string
  default     = "us-east-1"
}

# --- Red ---
variable "vpc_cidr" {
  description = "CIDR de la VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "azs" {
  description = "Zonas de disponibilidad a usar (mínimo 2 para Multi-AZ)."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.40.0.0/24", "10.40.1.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.40.10.0/24", "10.40.11.0/24"]
}

variable "database_subnet_cidrs" {
  type    = list(string)
  default = ["10.40.20.0/24", "10.40.21.0/24"]
}

# --- Dominio y TLS ---
variable "domain_name" {
  description = "Dominio raíz (ej: livemenu.app). Se deben crear registros CNAME manualmente si el DNS no está en Route53."
  type        = string
}

variable "app_subdomain" {
  description = "Subdominio de la app (ALB)."
  type        = string
  default     = "app"
}

variable "cdn_subdomain" {
  description = "Subdominio del CDN de imágenes."
  type        = string
  default     = "cdn"
}

variable "route53_zone_id" {
  description = "ID de la zona Route53 pública. Vacío para omitir creación de registros."
  type        = string
  default     = ""
}

# --- Base de datos ---
variable "db_name" {
  type    = string
  default = "livemenu_db"
}

variable "db_username" {
  type    = string
  default = "livemenu"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "db_allocated_storage" {
  type    = number
  default = 50
}

variable "db_backup_retention_days" {
  description = "Retención de backups diarios (mínimo 15 por política)."
  type        = number
  default     = 15
}

# --- Imágenes ECR (deben existir y contener tags antes de aplicar el servicio) ---
variable "backend_image_tag" {
  type    = string
  default = "latest"
}

variable "frontend_image_tag" {
  type    = string
  default = "latest"
}

# --- Fargate sizing ---
variable "backend_cpu" {
  type    = number
  default = 512
}

variable "backend_memory" {
  type    = number
  default = 1024
}

variable "backend_desired_count" {
  type    = number
  default = 2
}

variable "frontend_cpu" {
  type    = number
  default = 256
}

variable "frontend_memory" {
  type    = number
  default = 512
}

variable "frontend_desired_count" {
  type    = number
  default = 2
}

# --- Rotación de secretos ---
variable "secret_rotation_days" {
  description = "Periodo de rotación automática (máximo 40 por política)."
  type        = number
  default     = 30
  validation {
    condition     = var.secret_rotation_days > 0 && var.secret_rotation_days <= 40
    error_message = "La rotación debe ser mayor a 0 y menor o igual a 40 días."
  }
}

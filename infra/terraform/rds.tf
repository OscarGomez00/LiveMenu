resource "aws_db_subnet_group" "db" {
  name       = "${local.name_prefix}-db-subnet"
  subnet_ids = aws_subnet.database[*].id
  tags       = { Name = "${local.name_prefix}-db-subnet" }
}

resource "aws_db_parameter_group" "pg16" {
  name   = "${local.name_prefix}-pg16"
  family = "postgres16"

  parameter {
    name  = "rds.force_ssl" # TLS obligatorio en toda conexión
    value = "1"
  }
}

resource "random_password" "db_master" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?" # RDS no permite /, @, ", espacio
}

resource "aws_db_instance" "postgres" {
  identifier     = "${local.name_prefix}-pg"
  engine         = "postgres"
  engine_version = "16.3"

  instance_class        = var.db_instance_class
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 4
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.db.arn

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_master.result
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.pg16.name

  multi_az                     = true
  publicly_accessible          = false
  deletion_protection          = true
  copy_tags_to_snapshot        = true
  performance_insights_enabled = true
  performance_insights_kms_key_id = aws_kms_key.db.arn
  auto_minor_version_upgrade   = true

  backup_retention_period = var.db_backup_retention_days # política mínima: 15
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:30-sun:05:30"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.name_prefix}-pg-final-${formatdate("YYYYMMDDhhmm", timestamp())}"

  lifecycle {
    ignore_changes = [final_snapshot_identifier, password]
  }
}

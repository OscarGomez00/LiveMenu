resource "aws_kms_key" "db" {
  description             = "${local.name_prefix} RDS at-rest"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "db" {
  name          = "alias/${local.name_prefix}-rds"
  target_key_id = aws_kms_key.db.key_id
}

resource "aws_kms_key" "s3" {
  description             = "${local.name_prefix} S3 at-rest"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${local.name_prefix}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

resource "aws_kms_key" "secrets" {
  description             = "${local.name_prefix} Secrets Manager"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${local.name_prefix}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

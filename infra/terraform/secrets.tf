# db_credentials (rotación single-user) y jwt_signing_key (rotación custom).
# Rotación máxima por política: 40 días.

resource "aws_secretsmanager_secret" "db" {
  name        = "${local.name_prefix}/db_credentials"
  description = "Credenciales PostgreSQL para el backend"
  kms_key_id  = aws_kms_key.secrets.arn

  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_initial" {
  secret_id = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({
    engine   = "postgres"
    username = aws_db_instance.postgres.username
    password = random_password.db_master.result
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = aws_db_instance.postgres.db_name
  })

  lifecycle {
    ignore_changes = [secret_string] # a partir de aquí la rota la Lambda
  }
}

data "archive_file" "db_rotation_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/db_rotation"
  output_path = "${path.module}/build/db_rotation.zip"
}

resource "aws_lambda_function" "db_rotation" {
  function_name = "${local.name_prefix}-db-rotation"
  role          = aws_iam_role.db_rotation_lambda.arn
  runtime       = "python3.11"
  handler       = "lambda_function.lambda_handler"
  filename      = data.archive_file.db_rotation_zip.output_path
  source_code_hash = data.archive_file.db_rotation_zip.output_base64sha256
  timeout       = 60
  memory_size   = 256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.rotation_lambda.id]
  }

  environment {
    variables = {
      SECRETS_MANAGER_ENDPOINT = "https://secretsmanager.${var.region}.amazonaws.com"
    }
  }
}

resource "aws_lambda_permission" "db_rotation_invoke" {
  statement_id  = "AllowSecretsManagerInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.db_rotation.function_name
  principal     = "secretsmanager.amazonaws.com"
}

resource "aws_secretsmanager_secret_rotation" "db" {
  secret_id           = aws_secretsmanager_secret.db.id
  rotation_lambda_arn = aws_lambda_function.db_rotation.arn

  rotation_rules {
    automatically_after_days = var.secret_rotation_days
  }

  depends_on = [
    aws_secretsmanager_secret_version.db_initial,
    aws_lambda_permission.db_rotation_invoke,
  ]
}

resource "aws_secretsmanager_secret" "jwt" {
  name        = "${local.name_prefix}/jwt_signing_key"
  description = "Llave de firma de JWT emitidos por el backend"
  kms_key_id  = aws_kms_key.secrets.arn

  recovery_window_in_days = 7
}

resource "random_password" "jwt_initial" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret_version" "jwt_initial" {
  secret_id = aws_secretsmanager_secret.jwt.id
  secret_string = jsonencode({
    SECRET_KEY = random_password.jwt_initial.result
    ALGORITHM  = "HS256"
  })
  lifecycle {
    ignore_changes = [secret_string]
  }
}

data "archive_file" "jwt_rotation_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/jwt_rotation"
  output_path = "${path.module}/build/jwt_rotation.zip"
}

resource "aws_lambda_function" "jwt_rotation" {
  function_name = "${local.name_prefix}-jwt-rotation"
  role          = aws_iam_role.jwt_rotation_lambda.arn
  runtime       = "python3.11"
  handler       = "lambda_function.lambda_handler"
  filename      = data.archive_file.jwt_rotation_zip.output_path
  source_code_hash = data.archive_file.jwt_rotation_zip.output_base64sha256
  timeout       = 30
  memory_size   = 128
}

resource "aws_lambda_permission" "jwt_rotation_invoke" {
  statement_id  = "AllowSecretsManagerInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.jwt_rotation.function_name
  principal     = "secretsmanager.amazonaws.com"
}

resource "aws_secretsmanager_secret_rotation" "jwt" {
  secret_id           = aws_secretsmanager_secret.jwt.id
  rotation_lambda_arn = aws_lambda_function.jwt_rotation.arn

  rotation_rules {
    automatically_after_days = var.secret_rotation_days
  }

  depends_on = [
    aws_secretsmanager_secret_version.jwt_initial,
    aws_lambda_permission.jwt_rotation_invoke,
  ]
}

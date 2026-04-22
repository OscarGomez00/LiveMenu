# LiveMenu · Infraestructura AWS (Terraform)

Despliega la plataforma SaaS multi-sucursal en AWS siguiendo los requerimientos
de la Fase: orquestación contenerizada, base de datos gestionada con alta
disponibilidad, almacenamiento de objetos versionado, cifrado en reposo y en
tránsito, y gestión de secretos con rotación automática.

## Arquitectura resultante

```
  Internet
     │ HTTPS (TLS 1.2+)
     ▼
 ┌──────────────────────────────┐            ┌──────────────────────┐
 │ CloudFront (cdn.<dominio>)   │◀──privado──│  S3 bucket (imagenes)│ KMS + Versionado
 └──────────────────────────────┘            └──────────────────────┘
                                                      ▲
 ┌──────────────────────────────┐                     │ put/get (boto3)
 │ ALB (app.<dominio>, 443)     │                     │
 │  · 80 → redirect 443         │                     │
 │  · / → frontend TG           │                     │
 │  · /api/*, /health → backend │                     │
 └──────────────────────────────┘                     │
     │ awsvpc (privada)                               │
     ▼                                                │
 ┌────────────────────┐   ┌────────────────────┐      │
 │ ECS Fargate        │   │ ECS Fargate        │──────┘
 │  frontend (nginx)  │   │  backend (FastAPI) │
 └────────────────────┘   └────────────────────┘
                                │
                                ▼
                        ┌───────────────────┐
                        │ RDS PostgreSQL    │  Multi-AZ, KMS, backups 15d, TLS forzado
                        └───────────────────┘

 AWS Secrets Manager:
   livemenu/db_credentials   ──rotación Lambda (single-user) cada N<=40 días
   livemenu/jwt_signing_key  ──rotación Lambda custom           cada N<=40 días
```

## Estructura de los módulos

| Archivo | Propósito |
| --- | --- |
| `versions.tf` | Provider AWS (region + us-east-1 para ACM de CloudFront). |
| `variables.tf` | Parámetros editables (dominio, tamaños, rotación…). |
| `vpc.tf` | VPC, subnets públicas/privadas/db, NAT GW, endpoint S3. |
| `security_groups.tf` | SGs ALB → ECS → RDS + SG para la Lambda de rotación. |
| `kms.tf` | KMS keys dedicadas para RDS, S3 y Secrets Manager. |
| `rds.tf` | PostgreSQL 16 Multi-AZ, cifrado, `rds.force_ssl=1`, backups diarios. |
| `s3.tf` | Bucket de imágenes: versionado, SSE-KMS, bloqueo público. |
| `cloudfront.tf` | Distribución HTTPS con OAC privado hacia S3. |
| `secrets.tf` | Secretos DB+JWT con rotación y Lambdas. |
| `iam.tf` | Roles de ejecución/tarea con permisos mínimos. |
| `ecr.tf` | Repos ECR (immutable tags + scan on push). |
| `ecs.tf` | Cluster, task defs, services, autoscaling y CloudWatch Logs. |
| `alb.tf` | ALB 80→443, ACM, listeners y reglas por path. |
| `lambda/*` | Código Python de las rotaciones. |

## Requisitos previos

1. AWS CLI autenticado con permisos suficientes (admin en una cuenta de trabajo).
2. Terraform ≥ 1.5.
3. (Opcional) Zona Route53 pública para tu dominio. Sin ella, el ALB se crea
   pero el listener HTTPS queda pendiente (el HTTPS requiere certificado ACM
   validado por DNS). Define `route53_zone_id` en `terraform.tfvars` para
   completarlo automáticamente.

## Pasos de despliegue

```powershell
# 1. Copiar variables
cd infra\terraform
copy terraform.tfvars.example terraform.tfvars   # editar dominio, tamaños, etc.

# 2. Empaquetar dependencias de la Lambda de rotación de DB (pg8000)
python -m pip install -r lambda\db_rotation\requirements.txt -t lambda\db_rotation

# 3. Init + plan + apply
terraform init
terraform plan  -out tfplan
terraform apply tfplan
```

Tras el primer apply, Terraform imprime los endpoints (`alb_dns_name`,
`cdn_url`, `rds_endpoint`, `ecr_backend_repo`, ...).

## Publicar las imágenes Docker

```powershell
# Login a ECR
aws ecr get-login-password --region us-east-1 | `
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Backend
docker build -f ..\..\backend\Dockerfile.prod -t livemenu-backend:v1.0.0 ..\..\backend
docker tag  livemenu-backend:v1.0.0 $ECR_BACKEND:v1.0.0
docker push $ECR_BACKEND:v1.0.0

# Frontend (el API_URL queda embebido en el bundle estático)
docker build -f ..\..\frontend\Dockerfile.prod `
  --build-arg VITE_API_URL=https://app.livemenu.app/api/v1 `
  -t livemenu-frontend:v1.0.0 ..\..\frontend
docker tag  livemenu-frontend:v1.0.0 $ECR_FRONTEND:v1.0.0
docker push $ECR_FRONTEND:v1.0.0

# Forzar nuevo despliegue
aws ecs update-service --cluster $CLUSTER --service livemenu-prod-backend  --force-new-deployment
aws ecs update-service --cluster $CLUSTER --service livemenu-prod-frontend --force-new-deployment
```

## Mapeo requerimiento → recurso

| Requerimiento | Implementación |
| --- | --- |
| Backend + frontend orquestados | ECS Fargate (2 servicios) detrás del ALB |
| PostgreSQL gestionada HA | `aws_db_instance.postgres` con `multi_az = true` |
| S3 para variantes de imagen | `aws_s3_bucket.images` + CloudFront OAC |
| Cifrado at-rest DB | `storage_encrypted = true`, KMS `aws_kms_key.db` |
| Cifrado at-rest bucket | `SSE-KMS` con `aws_kms_key.s3` |
| Cifrado en tránsito | ACM + ALB TLS1.2+, `rds.force_ssl=1`, CloudFront redirect-to-https, `FORCE_HTTPS` middleware opcional |
| Sin `.env` en prod | `DB_SECRET_ARN` / `JWT_SECRET_ARN` inyectados; `backend/app/core/secrets.py` lee desde Secrets Manager |
| Rotación automática ≤ 40 días | `aws_secretsmanager_secret_rotation` (DB + JWT), `secret_rotation_days` validado |
| IAM mínimo privilegio | `backend_task` sólo escribe su bucket y lee sus 2 secretos |
| Backups diarios ≥ 15 días | `backup_retention_period = var.db_backup_retention_days` (default 15) |
| Versionado de objetos | `aws_s3_bucket_versioning` + lifecycle 90 días |

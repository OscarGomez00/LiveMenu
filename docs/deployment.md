# Instrucciones de Deployment — LiveMenu

## Requisitos Previos

- [Docker](https://www.docker.com/) 24+ y [Docker Compose](https://docs.docker.com/compose/) v2+
- Git

---

## Deployment con Docker Compose (Recomendado)

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd live_menu
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo del backend y edita los valores:

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env` con los valores de producción:

```env
# Base de datos
POSTGRES_USER=livemenu
POSTGRES_PASSWORD=<contraseña-segura>
POSTGRES_DB=livemenu_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Seguridad — CAMBIA ESTA CLAVE EN PRODUCCIÓN
SECRET_KEY=<clave-secreta-minimo-32-caracteres>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS — URL del frontend en producción
BACKEND_CORS_ORIGINS=["https://tu-dominio.com"]

# Imágenes
MAX_IMAGE_SIZE=2097152
ALLOWED_IMAGE_TYPES=["image/jpeg","image/png","image/webp"]
IMAGE_QUALITY=80
DISH_IMAGE_SIZE=[800, 600]

# Worker Pool
IMAGE_WORKERS=2
IMAGE_QUEUE_SIZE=20

# Caché de menú (segundos)
MENU_CACHE_TTL_SECONDS=60
```

> ⚠️ **Nunca comitees el archivo `.env` con datos reales al repositorio.**

### 3. Levantar los servicios

```bash
docker compose up -d --build
```

Esto levanta:
- `livemenu-db` — PostgreSQL en el puerto `5432`
- `livemenu-backend` — FastAPI en el puerto `8000` (inicializa la BD automáticamente)
- `livemenu-frontend` — React/Nginx en el puerto `5173`

### 4. Verificar que todo funciona

```bash
# Estado de los contenedores
docker compose ps

# Logs en tiempo real
docker compose logs -f

# Health check del backend
curl http://localhost:8000/health
# → {"status":"healthy"}
```

### 5. Acceder a la aplicación

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/v1 |
| Swagger (API docs) | http://localhost:8000/api/v1/docs |

---

## Desarrollo Local (Sin Docker)

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# o: source venv/bin/activate  (Linux/Mac)

# Instalar dependencias
pip install -r requirements.txt

# Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con POSTGRES_HOST=localhost

# Inicializar base de datos (asegúrate de tener PostgreSQL corriendo)
python -m app.db.init_db

# Levantar servidor de desarrollo
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Copiar variables de entorno
cp .env.example .env
# Editar .env: VITE_API_URL=http://localhost:8000

# Instalar dependencias
npm install

# Servidor de desarrollo
npm run dev
```

Acceder en: http://localhost:5173

---

## Comandos Útiles de Docker

```bash
# Detener todos los servicios
docker compose down

# Detener y borrar volúmenes (⚠️ elimina datos de la BD)
docker compose down -v

# Reconstruir solo el backend
docker compose up -d --build backend

# Ejecutar comandos en el contenedor del backend
docker exec -it livemenu-backend bash

# Ver logs de un servicio específico
docker compose logs -f backend

# Reiniciar un servicio
docker compose restart backend
```

---

## Migraciones de Base de Datos

El proyecto usa **Alembic** para migraciones:

```bash
# Dentro del contenedor o con venv activado en /backend

# Crear nueva migración
alembic revision --autogenerate -m "descripcion del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

---

## Estructura de Archivos Generados en Producción

```
backend/
└── uploads/          # Imágenes de platos subidas (WebP)
    ├── dish-a1b2c3.webp
    └── ...
```

> Las imágenes se sirven como archivos estáticos en `http://localhost:8000/uploads/<filename>`.  
> En producción se recomienda usar un CDN o bucket S3 para almacenamiento persistente.

---

## Consideraciones de Producción

| Área | Recomendación |
|------|---------------|
| **SECRET_KEY** | Generar con `openssl rand -hex 32` |
| **HTTPS** | Colocar un reverse proxy (Nginx, Caddy) frente a los contenedores |
| **Imágenes** | Usar volumen Docker persistente o migrar a S3/GCS |
| **BD** | Hacer backups regulares del volumen `pgdata` |
| **CORS** | Configurar `BACKEND_CORS_ORIGINS` con el dominio real del frontend |
| **Rate Limit** | Ajustar `RATE_LIMIT_PER_MINUTE` según el tráfico esperado |
| **JWT Expiry** | Reducir `ACCESS_TOKEN_EXPIRE_MINUTES` según política de seguridad |

---

## Variables de Entorno — Referencia Completa

| Variable | Descripción | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Usuario de la base de datos | `livemenu` |
| `POSTGRES_PASSWORD` | Contraseña de la base de datos | `livemenu123` |
| `POSTGRES_DB` | Nombre de la base de datos | `livemenu_db` |
| `POSTGRES_HOST` | Host de PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5432` |
| `SECRET_KEY` | Clave para firmar JWT | *(requerida en prod)* |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `30` |
| `BACKEND_CORS_ORIGINS` | Lista JSON de orígenes CORS | `["http://localhost:5173"]` |
| `RATE_LIMIT_PER_MINUTE` | Límite de requests por IP | `100` |
| `MAX_IMAGE_SIZE` | Tamaño máximo de imagen en bytes | `2097152` (2 MB) |
| `IMAGE_QUALITY` | Calidad WebP (0–100) | `80` |
| `DISH_IMAGE_SIZE` | Dimensiones de salida en px | `[800, 600]` |
| `IMAGE_WORKERS` | Procesos del worker pool | `2` |
| `IMAGE_QUEUE_SIZE` | Slots máximos en cola de imágenes | `20` |
| `MENU_CACHE_TTL_SECONDS` | TTL del caché de menú | `60` |

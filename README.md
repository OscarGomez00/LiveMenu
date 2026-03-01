# LiveMenu

Sistema de menú digital para restaurantes con panel de administración y vista pública accesible por QR.

---

## Arquitectura

| Capa | Tecnología |
|------|-----------|
| **Frontend** | React 19 + Vite + Tailwind CSS + shadcn/ui |
| **Backend** | FastAPI (Python 3.11) + SQLAlchemy Async |
| **Base de datos** | PostgreSQL 16 |
| **Contenedores** | Docker Compose |

---

## Casos de Uso Implementados

| CU | Descripción |
|----|-------------|
| CU-01 | Registro y autenticación JWT |
| CU-02 | CRUD Restaurante (nombre, descripción, logo, horarios, contacto, slug) |
| CU-03 | CRUD Categorías (nombre, descripción, orden, activar/desactivar) |
| CU-04 | CRUD Platos (nombre, precio, imagen, disponibilidad, soft-delete) |
| CU-05 | Carga de imágenes (conversión a WebP via Worker Pool) |
| CU-06 | Menú público por slug (filtrado por disponible/activa, caché en memoria) |
| CU-07 | Generación de código QR (PNG/SVG, 4 tamaños, colores custom) |

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [docs/architecture.md](docs/architecture.md) | Diagrama de arquitectura, modelo ER, árbol de componentes |
| [docs/api.md](docs/api.md) | Referencia completa de la API REST con ejemplos |
| [docs/deployment.md](docs/deployment.md) | Instrucciones de deployment (Docker y local) |

---

## Despliegue con Docker

### Requisitos previos

- Docker y Docker Compose instalados

### Levantar el proyecto

```bash
# Clonar y entrar al directorio
cd live_menu

# Construir e iniciar los 3 servicios (db, backend, frontend)
docker compose up --build -d

# Verificar que los contenedores estén corriendo
docker compose ps
```

### Acceso

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend (API) | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/v1/docs |

### Variables de entorno

Las variables están preconfiguradas en `docker-compose.yml` para desarrollo:

| Variable | Valor por defecto |
|----------|-------------------|
| `POSTGRES_USER` | livemenu |
| `POSTGRES_PASSWORD` | livemenu123 |
| `POSTGRES_DB` | livemenu_db |
| `SECRET_KEY` | (incluida en compose) |

### Detener

```bash
docker compose down        # Detener contenedores
docker compose down -v     # Detener y borrar datos de BD
```

---

## Desarrollo Local (sin Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Linux/Mac
# o: .venv\Scripts\activate  (Windows)
pip install -r requirements.txt

# Necesitas PostgreSQL corriendo (o levanta solo la BD con Docker):
docker compose up db -d

# Inicializar BD y correr servidor
python -m app.db.init_db
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Tests

```bash
cd backend
pytest -v     # Usa SQLite in-memory, no necesita PostgreSQL
```

---

## API Endpoints Principales

### Autenticación
- `POST /api/v1/auth/register` — Registro de usuario
- `POST /api/v1/auth/login` — Login (retorna JWT)

### Admin (requieren JWT)
- `GET/POST/PUT/DELETE /api/v1/restaurants` — CRUD restaurante
- `GET/POST /api/v1/categories` — Listar/Crear categoría
- `PUT/DELETE /api/v1/categories/{id}` — Editar/Eliminar categoría
- `GET/POST /api/v1/admin/dishes` — Listar/Crear plato
- `PUT/DELETE /api/v1/admin/dishes/{id}` — Editar/Eliminar plato
- `PATCH /api/v1/admin/dishes/{id}/availability` — Alternar disponibilidad
- `POST /api/v1/upload/dish` — Subir imagen de plato
- `GET /api/v1/admin/qr` — Generar código QR (params: size, format, color, bg_color)

### Público
- `GET /api/v1/menu/{slug}` — Ver menú del restaurante

# LiveMenu Backend

API REST para gestor de menús digitales.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # Autenticación
│   │   │   ├── restaurants.py   # CRUD restaurantes
│   │   │   ├── categories.py    # CRUD categorías
│   │   │   ├── dishes.py        # CRUD platos
│   │   │   ├── menu.py          # Menú público
│   │   │   ├── qr.py            # Generación QR
│   │   │   ├── upload.py        # Subida imágenes
│   │   │   ├── analytics.py     # Analíticas
│   │   │   └── router.py        # Router principal
│   │   └── dependencies.py      # Dependencies FastAPI
│   ├── core/
│   │   ├── config.py            # Configuración
│   │   └── security.py          # JWT y passwords
│   ├── db/
│   │   ├── session.py           # Sesión SQLAlchemy
│   │   └── init_db.py           # Inicialización DB
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── category.py
│   │   └── dish.py
│   ├── schemas/                 # Modelos Pydantic
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── category.py
│   │   └── dish.py
│   ├── repositories/            # Acceso a datos
│   ├── services/                # Lógica de negocio
│   ├── middlewares/             # Middlewares
│   └── workers/                 # Tareas background
├── tests/
├── main.py                      # Punto de entrada
└── requirements.txt

```

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Inicializar base de datos
python -m app.db.init_db

# Iniciar servidor
uvicorn main:app --reload --port 8000
```

## Tecnologías

- **FastAPI** - Framework web
- **PostgreSQL** - Base de datos
- **SQLAlchemy** (asyncpg) - ORM
- **JWT** - Autenticación
- **Bcrypt** - Hash de passwords
- **Pydantic** - Validación de datos

## Arquitectura

El proyecto sigue el patrón:
- **Models**: Modelos SQLAlchemy (base de datos)
- **Schemas**: Modelos Pydantic (validación)
- **Repositories**: Capa de acceso a datos
- **Services**: Lógica de negocio
- **API**: Endpoints REST

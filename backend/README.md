# LiveMenu Backend

API REST para gestor de menús digitales.

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

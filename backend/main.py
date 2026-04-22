from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from app.core.config import settings
from app.middlewares.rate_limit import RateLimitMiddleware
from app.api.v1.router import api_router
from fastapi.staticfiles import StaticFiles
from app.services.image_worker import image_pool
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Sólo montar /uploads cuando el storage es local (en prod las imágenes las sirve CloudFront).
if settings.STORAGE_BACKEND.lower() == "local":
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

if settings.FORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)

@app.on_event("startup")
async def startup_event():
    await image_pool.start()

@app.on_event("shutdown")
async def shutdown_event():
    await image_pool.stop()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Rate Limiting (100 requests/minuto)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)

# Incluir routers de API v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to LiveMenu API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

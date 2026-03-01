from fastapi import APIRouter

from app.api.v1 import (
    auth,
    menu,
    qr,
    upload,
)
from app.api.v1.admin.router import admin_router

api_router = APIRouter()

# Autenticación
api_router.include_router(auth.router)

# Rutas públicas
api_router.include_router(menu.router)

# Carga de imágenes (CU-05)
api_router.include_router(upload.router)

# QR (CU-07) - ya tiene prefix /admin/qr
api_router.include_router(qr.router)

# Administración (CU-02, CU-03, CU-04)
api_router.include_router(admin_router)

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.image_worker import image_pool
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["Carga de Archivos"])

@router.post("/dish")
async def upload_dish_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para cargar imágenes de platos.
    - Valida formato y tamaño.
    - Encola en el Worker Pool para procesamiento CPU-bound.
    - Convierte a WebP.
    - Retorna la URL relativa para guardar en el plato.
    """
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato no permitido. Use: {settings.ALLOWED_IMAGE_TYPES}"
        )
        
    # Validar tamaño (máximo definido en config)
    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Archivo demasiado grande. Máximo: {settings.MAX_IMAGE_SIZE // (1024*1024)}MB"
        )
    
    # Volver al inicio del archivo después de leerlo para que PIL pueda abrirlo en el worker
    await file.seek(0)
    
    # Encolar y esperar procesamiento
    url = await image_pool.enqueue_dish_image(content)
    
    return {"url": url}

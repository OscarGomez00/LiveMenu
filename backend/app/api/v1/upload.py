from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.image_worker import image_pool
from app.services.storage import get_storage
from app.core.config import settings

router = APIRouter(prefix="/admin/upload", tags=["Carga de Archivos"])


@router.post("/dish")
async def upload_dish_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Cargar imagen de plato. Genera 3 variantes WebP:
    - thumbnail (150x150)
    - medium (400x400)
    - large (800x800)

    Retorna las URLs de cada variante.
    """
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Use: {settings.ALLOWED_IMAGE_TYPES}",
        )

    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Máximo: {settings.MAX_IMAGE_SIZE // (1024*1024)}MB",
        )

    # Encolar y esperar procesamiento de las 3 variantes
    urls = await image_pool.enqueue_dish_image(content)

    return {
        "url": urls["large"],           # Compatibilidad con frontend actual
        "thumbnail": urls["thumbnail"],
        "medium": urls["medium"],
        "large": urls["large"],
    }


@router.delete("/{filename}")
async def delete_upload(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Eliminar una imagen subida y sus variantes."""
    base_name = filename.rsplit("_", 1)[0] if "_" in filename else filename.replace(".webp", "")
    storage = get_storage()
    deleted = []

    for variant in ["thumbnail", "medium", "large"]:
        key = f"dishes/{base_name}_{variant}.webp"
        try:
            storage.delete(key)
            deleted.append(key)
        except Exception:
            pass

    if not deleted:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return {"message": "Imagen eliminada", "deleted_files": deleted}

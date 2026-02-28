import os
import uuid
from pathlib import Path
from PIL import Image
from fastapi import UploadFile
from app.core.config import settings

class ImageService:
    """
    Servicio para el procesamiento de imágenes utilizando Pillow.
    Se encarga de redimensionar y convertir imágenes al formato WebP.
    """
    
    def __init__(self):
        # Directorio base de cargas
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.dish_dir = self.upload_dir / "dishes"
        
        # Asegurar que los directorios existan
        self.dish_dir.mkdir(parents=True, exist_ok=True)

    async def save_dish_image(self, file: UploadFile) -> str:
        """
        Procesa y guarda una imagen de plato en formato WebP.
        
        Args:
            file: Archivo de imagen subido
            
        Returns:
            URL relativa del archivo guardado
        """
        # Generar nombre único con extensión .webp
        filename = f"{uuid.uuid4()}.webp"
        file_path = self.dish_dir / filename
        
        # Abrir imagen con Pillow
        img = Image.open(file.file)
        
        # Convertir a RGB si es necesario (ej: de RGBA o modo P)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Redimensionar manteniendo aspecto (thumbnail)
        img.thumbnail(settings.DISH_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Guardar como WebP optimizado
        img.save(file_path, "WEBP", quality=settings.IMAGE_QUALITY)
        
        # Retornar ruta relativa para acceso vía URL
        return f"/uploads/dishes/{filename}"

    def delete_image(self, relative_path: str):
        """
        Elimina físicamente una imagen del sistema de archivos.
        
        Args:
            relative_path: Ruta relativa almacenada en DB (ej: /uploads/dishes/uuid.webp)
        """
        if not relative_path:
            return
            
        # Limpiar la ruta para obtener el path real
        # Quitamos el primer slash si existe para que Path no lo tome redundante
        clean_path = relative_path.lstrip("/")
        
        # Usar el directorio de trabajo actual para asegurar resolución correcta si es relativo
        full_path = Path(os.getcwd()) / clean_path
        
        try:
            if full_path.exists():
                os.remove(full_path)
                print(f"DEBUG: Imagen eliminada correctamente: {full_path}")
        except Exception as e:
            print(f"ERROR: No se pudo eliminar la imagen {full_path}: {e}")

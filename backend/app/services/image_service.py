import io
import uuid
from PIL import Image
from fastapi import UploadFile
from app.core.config import settings
from app.services.storage import get_storage

class ImageService:
    def __init__(self):
        self.storage = get_storage()

    async def save_dish_image(self, file: UploadFile) -> str:
        img = Image.open(file.file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        max_size = getattr(settings, "DISH_IMAGE_SIZE", (800, 800))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=settings.IMAGE_QUALITY)

        key = f"dishes/{uuid.uuid4()}.webp"
        return self.storage.put_bytes(key, buf.getvalue(), "image/webp")

    def delete_image(self, relative_path: str):
        if not relative_path:
            return
        key = relative_path
        for prefix in ("/uploads/", f"{settings.CDN_BASE_URL or ''}/"):
            if prefix and key.startswith(prefix):
                key = key[len(prefix):]
                break
        key = key.lstrip("/")
        try:
            self.storage.delete(key)
        except Exception as e:
            print(f"ERROR: no se pudo eliminar {key}: {e}")

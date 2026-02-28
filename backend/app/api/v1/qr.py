"""
Endpoint de generación de códigos QR para restaurantes.
Genera un QR que apunta al menú público del restaurante.

Especificaciones del enunciado:
- Nivel de corrección de errores: H (30%)
- Tamaños: S(200x200), M(400x400), L(800x800), XL(1200x1200)
- Formatos: PNG, SVG
- URL codificada: https://{domain}/m/{slug}
- Personalización de color
"""
import io
from enum import Enum

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.repositories.restaurant_repository import RestaurantRepository
from app.core.config import settings

router = APIRouter(prefix="/admin/qr", tags=["QR Code"])


class QRSize(str, Enum):
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"


# Mapeo de tamaños a píxeles de salida
QR_SIZE_MAP = {
    QRSize.S: 200,
    QRSize.M: 400,
    QRSize.L: 800,
    QRSize.XL: 1200,
}


class QRFormat(str, Enum):
    PNG = "png"
    SVG = "svg"


def _build_menu_url(slug: str) -> str:
    """Construye la URL pública del menú: https://{domain}/m/{slug}."""
    frontend_base = (
        settings.BACKEND_CORS_ORIGINS[0]
        if settings.BACKEND_CORS_ORIGINS
        else "http://localhost:5173"
    )
    return f"{frontend_base}/m/{slug}"


@router.get("")
async def generate_qr(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    size: QRSize = Query(QRSize.M, description="Tamaño del QR: s, m, l, xl"),
    format: QRFormat = Query(QRFormat.PNG, description="Formato de salida: png, svg"),
    color: str = Query("000000", description="Color del QR en HEX sin #"),
    bg_color: str = Query("FFFFFF", description="Color de fondo en HEX sin #"),
):
    """
    Genera un código QR que apunta al menú público del restaurante.

    - **size**: s (200px), m (400px), l (800px), xl (1200px)
    - **format**: png o svg
    - **color**: color del QR en hexadecimal (sin #), default negro
    - **bg_color**: color de fondo en hexadecimal (sin #), default blanco

    Requiere autenticación JWT.
    El QR usa nivel de corrección de errores H (30%).
    """
    # Obtener el restaurante del usuario autenticado
    restaurant_repo = RestaurantRepository(db)
    restaurants = await restaurant_repo.get_by_owner(current_user.id)

    if not restaurants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant found for this user",
        )

    restaurant = restaurants[0]
    menu_url = _build_menu_url(restaurant.slug)
    target_pixels = QR_SIZE_MAP[size]

    # Calcular box_size para alcanzar el tamaño deseado
    estimated_modules = 37
    box_size = max(1, round(target_pixels / estimated_modules))

    fill_color = f"#{color}"
    back_color = f"#{bg_color}"

    if format == QRFormat.SVG:
        return _generate_svg(menu_url, box_size, fill_color, back_color, restaurant.slug)
    else:
        return _generate_png(menu_url, box_size, fill_color, back_color, restaurant.slug, target_pixels)


def _generate_png(
    data: str,
    box_size: int,
    fill_color: str,
    back_color: str,
    slug: str,
    target_pixels: int,
) -> StreamingResponse:
    """Genera QR en formato PNG."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Redimensionar al tamaño exacto solicitado
    img = img.resize((target_pixels, target_pixels))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="qr-{slug}.png"'
        },
    )


def _generate_svg(
    data: str,
    box_size: int,
    fill_color: str,
    back_color: str,
    slug: str,
) -> StreamingResponse:
    """Genera QR en formato SVG."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    factory = qrcode.image.svg.SvgPathImage
    img = qr.make_image(image_factory=factory)

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/svg+xml",
        headers={
            "Content-Disposition": f'inline; filename="qr-{slug}.svg"'
        },
    )

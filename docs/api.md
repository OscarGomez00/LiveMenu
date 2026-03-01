# Documentación de API — LiveMenu

**Base URL:** `http://localhost:8000/api/v1`  
**Documentación interactiva (Swagger):** `http://localhost:8000/api/v1/docs`  
**Versión:** 1.0.0

> **Nota:** los archivos de configuración de `main` usan el prefijo `/admin/` para restaurante y categorías (`/admin/restaurant`, `/admin/categories`). El backend puede diferir en su estado actual de desarrollo; los paths aquí reflejan las llamadas reales del frontend.

---

## Autenticación

Los endpoints protegidos requieren el header:

```
Authorization: Bearer <token>
```

El token se obtiene en `/auth/login` o `/auth/register`.

---

## Módulos

- [Autenticación](#autenticación-1)
- [Restaurante](#restaurante)
- [Categorías](#categorías)
- [Menú Público](#menú-público)
- [Platos (Admin)](#platos-admin)
- [Imágenes](#imágenes)
- [Código QR](#código-qr)

---

## Autenticación

### `POST /auth/register`
Registra un nuevo usuario y retorna un token JWT.

**Body:**
```json
{
  "email": "admin@restaurante.com",
  "password": "minimo8chars"
}
```

**Respuesta 201:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errores:**
- `400` — Email ya registrado
- `422` — Validación fallida (email inválido, contraseña corta)

---

### `POST /auth/login`
Inicia sesión con email y contraseña.

**Body:**
```json
{
  "email": "admin@restaurante.com",
  "password": "minimo8chars"
}
```

**Respuesta 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errores:**
- `401` — Credenciales incorrectas

---

### `POST /auth/refresh` 🔒
Renueva el token JWT actual.

**Respuesta 200:** Igual a `/login`

---

### `POST /auth/logout` 🔒
Confirma el cierre de sesión (el cliente debe eliminar el token).

**Respuesta 200:**
```json
{ "message": "Successfully logged out" }
```

---

### `GET /auth/me` 🔒
Obtiene información del usuario autenticado.

**Respuesta 200:**
```json
{
  "id": "uuid",
  "email": "admin@restaurante.com"
}
```

---

## Restaurante

### `GET /admin/restaurant` 🔒
Obtiene el restaurante del usuario autenticado.

**Respuesta 200:**
```json
{
  "id": "uuid",
  "nombre": "La Buena Mesa",
  "slug": "la-buena-mesa",
  "descripcion": "Cocina casera tradicional",
  "logo_url": "/uploads/logo.webp",
  "telefono": "+57 300 000 0000",
  "direccion": "Calle 10 #20-30",
  "horarios": { "lunes": "12:00-22:00" }
}
```

**Errores:**
- `404` — Sin restaurante registrado

---

### `POST /admin/restaurant` 🔒
Crea el perfil del restaurante. El `slug` se genera automáticamente desde el `nombre`.

**Body:**
```json
{
  "nombre": "La Buena Mesa",
  "descripcion": "Cocina casera tradicional",
  "telefono": "+57 300 000 0000",
  "direccion": "Calle 10 #20-30",
  "horarios": { "lunes": "12:00-22:00" }
}
```

**Respuesta 201:** Objeto `RestaurantResponse`

**Errores:**
- `400` — Nombre/slug ya en uso

---

### `PUT /admin/restaurant` 🔒
Actualiza los datos del restaurante. Todos los campos son opcionales. Si se cambia el `nombre`, el `slug` se recalcula.

**Body:** Igual a `POST`, todos los campos opcionales

**Respuesta 200:** Objeto `RestaurantResponse`

---

### `DELETE /admin/restaurant` 🔒
Elimina el restaurante del usuario autenticado.

**Respuesta 204:** Sin contenido

---

## Categorías

### `GET /admin/categories` 🔒
Lista todas las categorías del restaurante autenticado.

**Respuesta 200:** `Array<CategoryResponse>`

---

### `POST /admin/categories` 🔒
Crea una nueva categoría.

**Body:**
```json
{
  "nombre": "Entradas",
  "restaurant_id": "uuid"
}
```

**Respuesta 201:** `CategoryResponse`

---

### `PUT /admin/categories/{id}` 🔒
Edita una categoría existente.

---

### `DELETE /admin/categories/{id}` 🔒
Elimina una categoría (solo si no tiene platos asociados).

**Respuesta 204:** Sin contenido

---

### `PATCH /admin/categories/reorder` 🔒
Reordena las categorías.

**Body:**
```json
{ "ordered_ids": ["uuid1", "uuid2", "uuid3"] }
```

**Respuesta 200:** Lista actualizada de categorías

---

## Menú Público

### `GET /menu/{slug}`
Obtiene el menú completo de un restaurante. **Endpoint público, no requiere autenticación.**

Usa caché en memoria con TTL de 60 segundos (configurable con `MENU_CACHE_TTL_SECONDS`).

**Path params:**
- `slug` — Identificador único del restaurante (ej: `la-buena-mesa`)

**Respuesta 200:**
```json
{
  "source": "db",
  "data": {
    "restaurant": { ... },
    "categories": [
      {
        "id": "uuid",
        "nombre": "Entradas",
        "dishes": [
          {
            "id": "uuid",
            "nombre": "Ensalada César",
            "descripcion": "Lechuga, crutones, parmesano",
            "precio": "12.50",
            "precio_oferta": null,
            "imagen_url": "/uploads/plato.webp",
            "disponible": true,
            "destacado": false,
            "etiquetas": ["vegetariano"]
          }
        ]
      }
    ]
  }
}
```

El campo `source` es `"cache"` cuando se sirve desde caché o `"db"` cuando se consultó la base de datos.

**Errores:**
- `404` — Restaurante no encontrado

---

## Platos (Admin)

Todos los endpoints de esta sección requieren autenticación JWT. 🔒

**Base path:** `/admin/dishes`

---

### `GET /admin/dishes`
Lista platos con filtros y paginación.

**Query params:**

| Parámetro | Tipo | Descripción | Default |
|-----------|------|-------------|---------|
| `skip` | int ≥ 0 | Offset de paginación | 0 |
| `limit` | int 1–500 | Máximo de resultados | 100 |
| `category_id` | UUID | Filtrar por categoría | — |
| `disponible` | bool | Filtrar por disponibilidad | — |
| `destacado` | bool | Filtrar por destacado | — |

**Respuesta 200:**
```json
{
  "total": 42,
  "skip": 0,
  "limit": 100,
  "dishes": [ ... ]
}
```

---

### `GET /admin/dishes/{id}`
Obtiene un plato por su UUID.

**Respuesta 200:** `DishResponse`

**Errores:**
- `404` — Plato no encontrado

---

### `POST /admin/dishes`
Crea un nuevo plato.

**Body:**
```json
{
  "nombre": "Ensalada César",
  "descripcion": "Lechuga, crutones, parmesano (máx 300 chars)",
  "precio": 12.50,
  "precio_oferta": 10.00,
  "category_id": "uuid-categoria",
  "imagen_url": "/uploads/plato-abc123.webp",
  "disponible": true,
  "destacado": false,
  "etiquetas": ["vegetariano", "sin gluten"],
  "posicion": 1
}
```

**Campos requeridos:** `nombre`, `precio`, `category_id`  
**Validación:** `precio_oferta` debe ser ≤ `precio`.

**Respuesta 201:** `DishResponse`

---

### `PUT /admin/dishes/{id}`
Actualiza un plato existente. Todos los campos son opcionales (PATCH semántico).

**Body:** Igual a `POST`, todos los campos opcionales

**Respuesta 200:** `DishResponse`

---

### `DELETE /admin/dishes/{id}`
Elimina un plato (soft delete — registra `eliminado_en`, no borra de la BD).

**Respuesta 200:**
```json
{ "message": "Dish deleted successfully" }
```

---

### `PATCH /admin/dishes/{id}/availability`
Alterna la disponibilidad del plato (`disponible: true ↔ false`).

**Respuesta 200:** `DishResponse` con el campo `disponible` actualizado

---

## Imágenes

### `POST /upload/dish` 🔒
Sube una imagen de plato. La imagen es procesada por el Worker Pool, convertida a WebP y almacenada en `/uploads/`.

**Content-Type:** `multipart/form-data`

**Form fields:**
- `file` — Archivo de imagen

**Restricciones:**
- Formatos permitidos: `image/jpeg`, `image/png`, `image/webp`
- Tamaño máximo: **2 MB**
- Salida: WebP, calidad 80%, redimensionado a **800×600 px**

**Respuesta 200:**
```json
{
  "url": "/uploads/dish-a1b2c3d4.webp"
}
```

**Errores:**
- `400` — Formato no permitido
- `400` — Archivo demasiado grande

Las imágenes son accesibles en `http://localhost:8000/uploads/<filename>`.

---

## Código QR

### `GET /admin/qr` 🔒
Genera un código QR que apunta al menú público del restaurante autenticado.

La URL codificada en el QR es: `{FRONTEND_URL}/m/{slug}`

**Query params:**

| Parámetro | Valores | Default | Descripción |
|-----------|---------|---------|-------------|
| `size` | `s`, `m`, `l`, `xl` | `m` | 200×200, 400×400, 800×800, 1200×1200 px |
| `format` | `png`, `svg` | `png` | Formato de imagen |
| `color` | HEX sin `#` | `000000` | Color del QR |
| `bg_color` | HEX sin `#` | `FFFFFF` | Color de fondo |

**Ejemplo:**
```
GET /api/v1/admin/qr?size=l&format=png&color=1a1a2e&bg_color=FFFFFF
```

**Respuesta 200:** Imagen binaria (`image/png` o `image/svg+xml`) con header:
```
Content-Disposition: inline; filename="qr-{slug}.png"
```

**Errores:**
- `404` — Sin restaurante registrado

---

## Modelos de Datos

### DishResponse

```typescript
{
  id: string;          // UUID
  nombre: string;
  descripcion: string | null;
  precio: string;      // Decimal (ej: "12.50")
  precio_oferta: string | null;
  category_id: string; // UUID
  imagen_url: string | null;
  disponible: boolean;
  destacado: boolean;
  etiquetas: string[] | null;
  posicion: number | null;
  creado_en: string;   // ISO 8601
  actualizado_en: string;
  eliminado_en: string | null;
}
```

### RestaurantResponse

```typescript
{
  id: string;
  nombre: string;
  slug: string;
  descripcion: string | null;
  logo_url: string | null;
  telefono: string | null;
  direccion: string | null;
  horarios: object | null;
}
```

### CategoryResponse

```typescript
{
  id: string;
  nombre: string;
  restaurant_id: string;
}
```

---

## Códigos de Error HTTP

| Código | Significado |
|--------|-------------|
| `400` | Bad Request — datos inválidos |
| `401` | Unauthorized — token ausente o inválido |
| `404` | Not Found — recurso no encontrado |
| `422` | Unprocessable Entity — error de validación Pydantic |
| `429` | Too Many Requests — rate limit excedido (100 req/min) |
| `500` | Internal Server Error |

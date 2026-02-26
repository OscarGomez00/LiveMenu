# Migraciones de Base de Datos

Este directorio contiene las migraciones SQL para la base de datos de LiveMenu.

## Ejecución de Migraciones

### Aplicar migración

```bash
# Conectarse a PostgreSQL
psql -U postgres -d live_menu -f migrations/001_add_dish_fields.sql
```

### Revertir migración (rollback)

```bash
psql -U postgres -d live_menu -f migrations/001_add_dish_fields_rollback.sql
```

## Lista de Migraciones

- **001_add_dish_fields.sql**: Agrega campos completos al modelo Dish (descripcion, precio_oferta, imagen_url, disponible, destacado, etiquetas, posicion, timestamps, soft delete)

## Notas

- Siempre hacer backup de la base de datos antes de aplicar migraciones
- Los scripts de rollback permiten revertir cambios si es necesario
- Los índices creados mejoran el rendimiento de consultas frecuentes

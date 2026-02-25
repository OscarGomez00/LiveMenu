"""
Servicio para lógica de negocio de platos.
Implementa validaciones y operaciones específicas del dominio.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.dish_repository import DishRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.dish import DishCreate, DishUpdate, DishResponse, DishListResponse
from app.models.dish import Dish


class DishService:
    """Servicio para gestionar lógica de negocio de platos."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializar servicio con sesión de base de datos.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        self.db = db
        self.dish_repo = DishRepository(db)
    
    async def get_dishes(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[UUID] = None,
        disponible: Optional[bool] = None,
        destacado: Optional[bool] = None
    ) -> DishListResponse:
        """
        Obtener lista paginada de platos con filtros.
        
        Args:
            skip: Offset para paginación
            limit: Límite de resultados
            category_id: Filtrar por categoría
            disponible: Filtrar por disponibilidad
            destacado: Filtrar por destacado
            
        Returns:
            Lista paginada de platos
        """
        dishes, total = await self.dish_repo.get_all(
            skip=skip,
            limit=limit,
            category_id=category_id,
            disponible=disponible,
            destacado=destacado
        )
        
        return DishListResponse(
            total=total,
            skip=skip,
            limit=limit,
            dishes=[DishResponse.model_validate(dish) for dish in dishes]
        )
    
    async def get_dish_by_id(self, dish_id: UUID) -> DishResponse:
        """
        Obtener un plato por su ID.
        
        Args:
            dish_id: UUID del plato
            
        Returns:
            Datos del plato
            
        Raises:
            HTTPException: Si el plato no existe
        """
        dish = await self.dish_repo.get_by_id(dish_id)
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plato con ID {dish_id} no encontrado"
            )
        
        return DishResponse.model_validate(dish)
    
    async def create_dish(self, dish_data: DishCreate) -> DishResponse:
        """
        Crear un nuevo plato con validaciones de negocio.
        
        Args:
            dish_data: Datos del plato a crear
            
        Returns:
            Plato creado
            
        Raises:
            HTTPException: Si la categoría no existe o datos inválidos
        """
        # Validar que la categoría existe
        from app.repositories.category_repository import CategoryRepository
        category_repo = CategoryRepository(self.db)
        category = await category_repo.get_by_id(dish_data.category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {dish_data.category_id} no encontrada"
            )
        
        # Validación adicional: precio_oferta debe ser menor que precio
        if dish_data.precio_oferta is not None:
            if dish_data.precio_oferta > dish_data.precio:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio de oferta debe ser menor o igual al precio normal"
                )
        
        # Crear plato
        dish = await self.dish_repo.create(dish_data.model_dump())
        
        # TODO: Invalidar caché del menú público
        # await self._invalidate_menu_cache()
        
        return DishResponse.model_validate(dish)
    
    async def update_dish(
        self,
        dish_id: UUID,
        dish_data: DishUpdate
    ) -> DishResponse:
        """
        Actualizar un plato existente con validaciones.
        
        Args:
            dish_id: UUID del plato a actualizar
            dish_data: Datos a actualizar
            
        Returns:
            Plato actualizado
            
        Raises:
            HTTPException: Si el plato no existe o datos inválidos
        """
        # Verificar que el plato existe
        existing_dish = await self.dish_repo.get_by_id(dish_id)
        if not existing_dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plato con ID {dish_id} no encontrado"
            )
        
        # Si se actualiza la categoría, validar que existe
        if dish_data.category_id is not None:
            from app.repositories.category_repository import CategoryRepository
            category_repo = CategoryRepository(self.db)
            category = await category_repo.get_by_id(dish_data.category_id)
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Categoría con ID {dish_data.category_id} no encontrada"
                )
        
        # Validar precio_oferta vs precio
        precio_final = dish_data.precio if dish_data.precio is not None else existing_dish.precio
        precio_oferta_final = dish_data.precio_oferta if dish_data.precio_oferta is not None else existing_dish.precio_oferta
        
        if precio_oferta_final is not None and precio_oferta_final > precio_final:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio de oferta debe ser menor o igual al precio normal"
            )
        
        # Actualizar solo campos no None
        update_data = dish_data.model_dump(exclude_unset=True)
        dish = await self.dish_repo.update(dish_id, update_data)
        
        # TODO: Invalidar caché del menú público
        # await self._invalidate_menu_cache()
        
        return DishResponse.model_validate(dish)
    
    async def delete_dish(self, dish_id: UUID) -> dict:
        """
        Realizar soft delete de un plato.
        
        Args:
            dish_id: UUID del plato a eliminar
            
        Returns:
            Mensaje de confirmación
            
        Raises:
            HTTPException: Si el plato no existe
        """
        dish = await self.dish_repo.soft_delete(dish_id)
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plato con ID {dish_id} no encontrado"
            )
        
        # TODO: Invalidar caché del menú público
        # await self._invalidate_menu_cache()
        
        return {
            "message": "Plato eliminado exitosamente",
            "dish_id": str(dish_id)
        }
    
    async def toggle_dish_availability(self, dish_id: UUID) -> DishResponse:
        """
        Alternar disponibilidad de un plato.
        
        Args:
            dish_id: UUID del plato
            
        Returns:
            Plato con disponibilidad actualizada
            
        Raises:
            HTTPException: Si el plato no existe
        """
        dish = await self.dish_repo.toggle_availability(dish_id)
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plato con ID {dish_id} no encontrado"
            )
        
        # TODO: Invalidar caché del menú público
        # await self._invalidate_menu_cache()
        
        return DishResponse.model_validate(dish)
    
    async def get_dishes_by_category(
        self,
        category_id: UUID,
        disponible_only: bool = True
    ) -> List[DishResponse]:
        """
        Obtener todos los platos de una categoría.
        
        Args:
            category_id: UUID de la categoría
            disponible_only: Solo platos disponibles
            
        Returns:
            Lista de platos de la categoría
        """
        dishes = await self.dish_repo.get_by_category(
            category_id=category_id,
            disponible_only=disponible_only
        )
        
        return [DishResponse.model_validate(dish) for dish in dishes]
    
    # TODO: Implementar cuando se tenga sistema de caché
    # async def _invalidate_menu_cache(self):
    #     """Invalidar caché del menú público."""
    #     pass

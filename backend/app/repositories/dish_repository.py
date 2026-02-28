"""
Repositorio para operaciones de base de datos de Dish (Platos).
Implementa el patrón Repository para acceso a datos.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dish import Dish


class DishRepository:
    """Repositorio para gestionar operaciones CRUD de platos."""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializar repositorio con sesión de base de datos.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        self.db = db
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[UUID] = None,
        disponible: Optional[bool] = None,
        destacado: Optional[bool] = None,
        include_deleted: bool = False
    ) -> tuple[List[Dish], int]:
        """
        Obtener lista de platos con filtros opcionales y paginación.
        
        Args:
            skip: Número de registros a saltar (paginación)
            limit: Máximo número de registros a retornar
            category_id: Filtrar por categoría (opcional)
            disponible: Filtrar por disponibilidad (opcional)
            destacado: Filtrar por platos destacados (opcional)
            include_deleted: Incluir platos eliminados (soft delete)
            
        Returns:
            Tupla de (lista de platos, total de registros)
        """
        # Construcción de query base
        query = select(Dish)
        count_query = select(func.count(Dish.id))
        
        # Aplicar filtros
        filters = []
        
        if not include_deleted:
            filters.append(Dish.eliminado_en.is_(None))
        
        if category_id is not None:
            filters.append(Dish.category_id == category_id)
        
        if disponible is not None:
            filters.append(Dish.disponible == disponible)
        
        if destacado is not None:
            filters.append(Dish.destacado == destacado)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Ordenar por posición y nombre
        query = query.order_by(Dish.posicion.asc().nulls_last(), Dish.nombre)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar queries
        result = await self.db.execute(query)
        dishes = result.scalars().all()
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        return list(dishes), total
    
    async def get_by_id(self, dish_id: UUID) -> Optional[Dish]:
        """
        Obtener un plato por su ID (excluyendo soft-deleted).
        
        Args:
            dish_id: UUID del plato
            
        Returns:
            Plato si existe y no está eliminado, None en caso contrario
        """
        query = select(Dish).where(
            and_(
                Dish.id == dish_id,
                Dish.eliminado_en.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_category(
        self,
        category_id: UUID,
        disponible_only: bool = True
    ) -> List[Dish]:
        """
        Obtener todos los platos de una categoría.
        
        Args:
            category_id: UUID de la categoría
            disponible_only: Solo platos disponibles
            
        Returns:
            Lista de platos de la categoría
        """
        filters = [
            Dish.category_id == category_id,
            Dish.eliminado_en.is_(None)
        ]
        
        if disponible_only:
            filters.append(Dish.disponible == True)
        
        query = select(Dish).where(and_(*filters)).order_by(
            Dish.posicion.asc().nulls_last(),
            Dish.nombre
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, dish_data: dict) -> Dish:
        """
        Crear un nuevo plato.
        
        Args:
            dish_data: Diccionario con datos del plato
            
        Returns:
            Plato creado
        """
        # Si no se proporciona posición, calcular la siguiente
        if 'posicion' not in dish_data or dish_data['posicion'] is None:
            max_position_query = select(func.max(Dish.posicion)).where(
                Dish.category_id == dish_data['category_id']
            )
            result = await self.db.execute(max_position_query)
            max_position = result.scalar()
            dish_data['posicion'] = (max_position or 0) + 1
        
        dish = Dish(**dish_data)
        self.db.add(dish)
        await self.db.commit()
        await self.db.refresh(dish)
        return dish
    
    async def update(self, dish_id: UUID, dish_data: dict) -> Optional[Dish]:
        """
        Actualizar un plato existente.
        
        Args:
            dish_id: UUID del plato
            dish_data: Diccionario con datos a actualizar
            
        Returns:
            Plato actualizado o None si no existe
        """
        dish = await self.get_by_id(dish_id)
        if not dish:
            return None
        
        # Actualizar solo campos proporcionados
        for key, value in dish_data.items():
            if hasattr(dish, key):
                setattr(dish, key, value)
        
        await self.db.commit()
        await self.db.refresh(dish)
        return dish
    
    async def soft_delete(self, dish_id: UUID) -> Optional[Dish]:
        """
        Realizar soft delete de un plato (marcar como eliminado).
        
        Args:
            dish_id: UUID del plato
            
        Returns:
            Plato eliminado o None si no existe
        """
        dish = await self.get_by_id(dish_id)
        if not dish:
            return None
        
        dish.eliminado_en = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(dish)
        return dish
    
    async def toggle_availability(self, dish_id: UUID) -> Optional[Dish]:
        """
        Alternar disponibilidad de un plato.
        
        Args:
            dish_id: UUID del plato
            
        Returns:
            Plato con disponibilidad actualizada o None si no existe
        """
        dish = await self.get_by_id(dish_id)
        if not dish:
            return None
        
        dish.disponible = not dish.disponible
        await self.db.commit()
        await self.db.refresh(dish)
        return dish
    
    async def reorder(self, dish_id: UUID, new_position: int) -> Optional[Dish]:
        """
        Actualizar la posición de un plato para ordenamiento.
        
        Args:
            dish_id: UUID del plato
            new_position: Nueva posición
            
        Returns:
            Plato con posición actualizada o None si no existe
        """
        dish = await self.get_by_id(dish_id)
        if not dish:
            return None
        
        dish.posicion = new_position
        await self.db.commit()
        await self.db.refresh(dish)
        return dish

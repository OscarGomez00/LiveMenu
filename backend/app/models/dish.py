import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, ForeignKey, Boolean, Integer, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base, GUID


class Dish(Base):
    __tablename__ = "dishes"
    
    # Identificador
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    
    # Información básica
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)  # Máx 300 caracteres (validado en schema)
    
    # Precios
    precio = Column(Numeric(10, 2), nullable=False)
    precio_oferta = Column(Numeric(10, 2), nullable=True)
    
    # Imagen
    imagen_url = Column(String, nullable=True)
    
    # Estados
    disponible = Column(Boolean, default=True, nullable=False)
    destacado = Column(Boolean, default=False, nullable=False)
    
    # Clasificación
    etiquetas = Column(JSON, nullable=True)  # Ej: ["vegetariano", "picante", "sin gluten"]
    posicion = Column(Integer, nullable=True)  # Para ordenamiento
    
    # Relaciones
    category_id = Column(GUID, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="dishes")
    
    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    eliminado_en = Column(DateTime, nullable=True)  # Soft delete
    
    def __repr__(self):
        return f"<Dish(id={self.id}, nombre={self.nombre}, precio={self.precio}, disponible={self.disponible})>"

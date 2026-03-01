import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base, GUID


class Category(Base):
    __tablename__ = "categories"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    posicion = Column(Integer, default=0, nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    restaurant_id = Column(GUID, ForeignKey("restaurants.id"), nullable=False)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    restaurant = relationship("Restaurant", back_populates="categories")
    dishes = relationship("Dish", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, nombre={self.nombre}, posicion={self.posicion})>"

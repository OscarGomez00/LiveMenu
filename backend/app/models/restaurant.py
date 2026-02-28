import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base, GUID

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String(100), nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    descripcion = Column(Text, nullable=True) # Validaremos los 500 caracteres en el Schema
    logo_url = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    horarios = Column(JSONB, nullable=True) # Tipo JSONB para flexibilidad
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    
    # Relaciones
    owner = relationship("User", back_populates="restaurants")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Restaurant(id={self.id}, nombre={self.nombre}, slug={self.slug})>"

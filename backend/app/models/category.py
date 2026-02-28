import uuid
from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db.session import Base, GUID

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False)
    restaurant_id = Column(GUID, ForeignKey("restaurants.id"), nullable=False)
    
    # Relaciones
    restaurant = relationship("Restaurant", back_populates="categories")
    dishes = relationship("Dish", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, nombre={self.nombre})>"

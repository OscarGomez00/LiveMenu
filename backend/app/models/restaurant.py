import uuid
from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db.session import Base, GUID

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    
    # Relaciones
    owner = relationship("User", back_populates="restaurants")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Restaurant(id={self.id}, nombre={self.nombre}, slug={self.slug})>"

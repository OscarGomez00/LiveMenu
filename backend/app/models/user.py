import uuid
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
from app.db.session import Base, GUID

class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Relación con Restaurant
    restaurants = relationship("Restaurant", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

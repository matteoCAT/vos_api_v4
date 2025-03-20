from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel


class Site(BaseModel):
    """Model for restaurant sites/locations"""

    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # FK to the manager of this site (optional)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id], back_populates="managed_sites")

    # Products and other relationships can be added here
    # products = relationship("Product", back_populates="site")
    # recipes = relationship("Recipe", back_populates="site")
    # invoices = relationship("Invoice", back_populates="site")
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class Supplier(BaseModel):
    """Supplier model"""

    name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    tax_id = Column(String(50), nullable=True, unique=True)
    website = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
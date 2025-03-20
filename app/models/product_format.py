from sqlalchemy import Column, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class ProductFormat(BaseModel):
    """
    Model for product formats (e.g., 0.5L, 1L, 280g, etc.)
    A format is a specific size or quantity of a product, with associated unit
    """

    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, nullable=True)

    # The numeric value of the format (e.g., 0.5, 1, 280)
    value = Column(Float, nullable=False)

    # Reference to the unit of measurement
    unit_id = Column(UUID(as_uuid=True), ForeignKey("productunit.id"), nullable=False)
    unit = relationship("ProductUnit", backref="formats")

    # Whether this is a standard format that can be used for multiple products
    is_standard = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<ProductFormat {self.name} ({self.value})>"
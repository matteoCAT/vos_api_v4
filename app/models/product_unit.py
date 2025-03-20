from sqlalchemy import Column, String, Boolean

from app.models.base import BaseModel


class ProductUnit(BaseModel):
    """Model for product measurement units (e.g., kg, liter, bottle, case, etc.)"""

    name = Column(String, index=True, nullable=False, unique=True)
    symbol = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_base_unit = Column(Boolean, default=False, nullable=False)

    # If this unit can be used for purchase
    purchasable = Column(Boolean, default=True, nullable=False)

    # If this unit can be used for sales
    sellable = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<ProductUnit {self.name} ({self.symbol})>"
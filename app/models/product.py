from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.models.base import BaseModel


class ProductType(str, enum.Enum):
    """Enumeration of product types"""
    UNIT = "unit"  # Products sold by unit (e.g., bottled water)
    CASE = "case"  # Products sold in cases/packs (e.g., canned tuna)
    WEIGHT = "weight"  # Products sold by weight (e.g., ham)


class Product(BaseModel):
    """
    Model for products with different measurement types
    """

    name = Column(String, index=True, nullable=False)
    code = Column(String, index=True, nullable=True, unique=True)
    description = Column(String, nullable=True)

    # Product type determines how the product is measured and sold
    product_type = Column(Enum(ProductType), nullable=False, index=True)

    # Base price is always per purchase unit
    base_price = Column(Float, nullable=False, default=0.0)

    # For products that are sold by weight, we store the price per kg
    price_per_kg = Column(Float, nullable=True)

    # Is this product active and available for sale/purchase?
    is_active = Column(Boolean, default=True, nullable=False)

    # Is this product available for purchase?
    purchasable = Column(Boolean, default=True, nullable=False)

    # Is this product available for sale?
    sellable = Column(Boolean, default=True, nullable=False)

    # Default purchase unit (e.g., case, kg)
    purchase_unit_id = Column(UUID(as_uuid=True), ForeignKey("productunit.id"), nullable=False)
    purchase_unit = relationship("ProductUnit", foreign_keys=[purchase_unit_id], backref="purchased_products")

    # Default sales unit (e.g., bottle, gram)
    sales_unit_id = Column(UUID(as_uuid=True), ForeignKey("productunit.id"), nullable=False)
    sales_unit = relationship("ProductUnit", foreign_keys=[sales_unit_id], backref="sold_products")

    # Default format for this product (e.g., 0.5L bottle)
    default_format_id = Column(UUID(as_uuid=True), ForeignKey("productformat.id"), nullable=True)
    default_format = relationship("ProductFormat", backref="products")

    # Conversion factor between purchase and sales unit
    # E.g., if purchase_unit is case and sales_unit is bottle,
    # conversion_factor might be 12 (12 bottles per case)
    conversion_factor = Column(Float, nullable=False, default=1.0)

    def __repr__(self):
        return f"<Product {self.name} ({self.product_type})>"
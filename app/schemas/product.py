from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from app.models.product import ProductType
from app.schemas.product_unit import ProductUnit
from app.schemas.product_format import ProductFormat


class ProductBase(BaseModel):
    """Base schema for Product data"""
    name: str = Field(..., description="Product name")
    code: Optional[str] = Field(None, description="Product code")
    description: Optional[str] = Field(None, description="Product description")
    product_type: ProductType = Field(..., description="Product type (unit, case, weight)")
    base_price: float = Field(..., description="Base price per purchase unit")
    vat_rate: Decimal = Field(20.0, description="VAT rate in percentage (e.g., 20.0 for 20%)")
    price_per_kg: Optional[float] = Field(None, description="Price per kg for weight-based products")
    is_active: Optional[bool] = Field(True, description="Whether the product is active")
    purchasable: Optional[bool] = Field(True, description="Whether the product can be purchased")
    sellable: Optional[bool] = Field(True, description="Whether the product can be sold")
    purchase_unit_id: UUID = Field(..., description="ID of the purchase unit")
    sales_unit_id: UUID = Field(..., description="ID of the sales unit")
    default_format_id: Optional[UUID] = Field(None, description="ID of the default format")
    conversion_factor: Optional[float] = Field(1.0, description="Conversion factor between purchase and sales unit")

    @validator('price_per_kg')
    def validate_price_per_kg(cls, v, values):
        if values.get('product_type') == ProductType.WEIGHT and v is None:
            raise ValueError('price_per_kg is required for weight-based products')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product"""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bottled Water",
                "code": "BW001",
                "description": "Natural spring water",
                "product_type": "unit",
                "base_price": 10.99,
                "vat_rate": 20.0,
                "is_active": True,
                "purchasable": True,
                "sellable": True,
                "purchase_unit_id": "00000000-0000-0000-0000-000000000000",
                "sales_unit_id": "00000000-0000-0000-0000-000000000000",
                "default_format_id": "00000000-0000-0000-0000-000000000000",
                "conversion_factor": 12.0
            }
        }


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    product_type: Optional[ProductType] = None
    base_price: Optional[float] = None
    vat_rate: Optional[Decimal] = None
    price_per_kg: Optional[float] = None
    is_active: Optional[bool] = None
    purchasable: Optional[bool] = None
    sellable: Optional[bool] = None
    purchase_unit_id: Optional[UUID] = None
    sales_unit_id: Optional[UUID] = None
    default_format_id: Optional[UUID] = None
    conversion_factor: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Water",
                "description": "Premium natural spring water",
                "base_price": 12.99,
                "vat_rate": 5.0,
                "is_active": False
            }
        }


class ProductInDBBase(ProductBase):
    """Schema for Product data as stored in DB"""
    id: UUID

    class Config:
        from_attributes = True


class Product(ProductInDBBase):
    """Schema for Product data returned to client"""
    pass


class ProductDetail(Product):
    """Schema for Product data with related entity details"""
    purchase_unit: ProductUnit
    sales_unit: ProductUnit
    default_format: Optional[ProductFormat] = None

    class Config:
        from_attributes = True


class ProductResponse(ProductInDBBase):
    """Schema for Product data returned to client with additional fields for UI display"""
    # Include original IDs
    purchase_unit_id: UUID
    sales_unit_id: UUID
    default_format_id: Optional[UUID] = None

    # Add string representations for UI display
    purchase_unit_name: str
    purchase_unit_symbol: str
    sales_unit_name: str
    sales_unit_symbol: str
    default_format_name: Optional[str] = None

    class Config:
        from_attributes = True
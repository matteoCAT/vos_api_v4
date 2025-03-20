from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.schemas.product_unit import ProductUnit


class ProductFormatBase(BaseModel):
    """Base schema for Product Format data"""
    name: str = Field(..., description="Format name (e.g., '0.5L Bottle', '280g Can')")
    description: Optional[str] = Field(None, description="Format description")
    value: float = Field(..., description="Numeric value of the format")
    unit_id: UUID = Field(..., description="ID of the associated unit")
    is_standard: Optional[bool] = Field(True, description="Whether this is a standard format")


class ProductFormatCreate(ProductFormatBase):
    """Schema for creating a new product format"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "0.5L Bottle",
                "description": "Standard half-liter bottle",
                "value": 0.5,
                "unit_id": "00000000-0000-0000-0000-000000000000",
                "is_standard": True
            }
        }


class ProductFormatUpdate(BaseModel):
    """Schema for updating a product format"""
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    unit_id: Optional[UUID] = None
    is_standard: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "0.5L Bottle",
                "description": "Updated description",
                "value": 0.5,
                "is_standard": False
            }
        }


class ProductFormatInDBBase(ProductFormatBase):
    """Schema for Product Format data as stored in DB"""
    id: UUID

    class Config:
        from_attributes = True


class ProductFormat(ProductFormatInDBBase):
    """Schema for Product Format data returned to client"""
    pass


class ProductFormatDetail(ProductFormat):
    """Schema for Product Format data with unit details"""
    unit: ProductUnit
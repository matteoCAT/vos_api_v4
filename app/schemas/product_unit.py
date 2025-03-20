from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ProductUnitBase(BaseModel):
    """Base schema for Product Unit data"""
    name: str = Field(..., description="Unit name (e.g., kilogram, liter, bottle)")
    symbol: str = Field(..., description="Unit symbol (e.g., kg, L, btl)")
    description: Optional[str] = Field(None, description="Unit description")
    is_base_unit: Optional[bool] = Field(False, description="Whether this is a base unit")
    purchasable: Optional[bool] = Field(True, description="Whether this unit can be used for purchasing")
    sellable: Optional[bool] = Field(True, description="Whether this unit can be used for selling")


class ProductUnitCreate(ProductUnitBase):
    """Schema for creating a new product unit"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Kilogram",
                "symbol": "kg",
                "description": "Standard weight measurement",
                "is_base_unit": True,
                "purchasable": True,
                "sellable": True
            }
        }


class ProductUnitUpdate(BaseModel):
    """Schema for updating a product unit"""
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    is_base_unit: Optional[bool] = None
    purchasable: Optional[bool] = None
    sellable: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Kilogram",
                "symbol": "kg",
                "description": "Updated description",
                "purchasable": False
            }
        }


class ProductUnitInDBBase(ProductUnitBase):
    """Schema for Product Unit data as stored in DB"""
    id: UUID

    class Config:
        from_attributes = True


class ProductUnit(ProductUnitInDBBase):
    """Schema for Product Unit data returned to client"""
    pass
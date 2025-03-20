from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional
from uuid import UUID


class SupplierBase(BaseModel):
    """Base schema for Supplier data"""
    name: str
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True


class SupplierCreate(SupplierBase):
    """Schema for creating a new supplier"""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ABC Supplies Inc.",
                "contact_name": "John Smith",
                "email": "contact@abcsupplies.com",
                "phone": "+1234567890",
                "address": "123 Main St, Anytown, USA",
                "tax_id": "AB-12345678",
                "website": "https://www.abcsupplies.com",
                "notes": "Primary supplier for fresh ingredients",
                "is_active": True
            }
        }


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Supplies Inc.",
                "contact_name": "Jane Doe",
                "email": "jane@updatedsupplies.com",
                "phone": "+9876543210",
                "address": "456 Oak Ave, Newtown, USA",
                "is_active": True
            }
        }


class SupplierInDBBase(SupplierBase):
    """Schema for Supplier data as stored in DB"""
    id: UUID

    class Config:
        from_attributes = True


class Supplier(SupplierInDBBase):
    """Schema for Supplier data returned to client"""
    pass
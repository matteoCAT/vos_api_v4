from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class SiteBase(BaseModel):
    """Base schema for Site data"""
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True


class SiteCreate(SiteBase):
    """Schema for creating a new site"""
    manager_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Downtown Restaurant",
                "address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA",
                "phone": "+1234567890",
                "email": "downtown@restaurant.com",
                "is_active": True,
                "manager_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
            }
        }


class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    manager_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Restaurant Name",
                "address": "456 Oak Ave",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "country": "USA",
                "phone": "+9876543210",
                "email": "chicago@restaurant.com",
                "is_active": True,
                "manager_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
            }
        }


class SiteInDBBase(SiteBase):
    """Schema for Site data as stored in DB"""
    id: UUID
    manager_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class Site(SiteInDBBase):
    """Schema for Site data returned to client"""
    pass


class SiteWithDetails(Site):
    """Schema for Site data with manager details"""
    manager_name: Optional[str] = None
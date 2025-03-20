from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload"""
    sub: Optional[str] = None  # subject (user id)
    role: Optional[str] = None  # user role
    exp: Optional[int] = None  # expiration time


class TokenData(BaseModel):
    """Schema for token data extracted from JWT"""
    user_id: Optional[int] = None
    role: Optional[str] = None


class Login(BaseModel):
    """Schema for login request"""
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class RefreshToken(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str
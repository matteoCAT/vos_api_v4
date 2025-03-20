from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    users,
    suppliers,
    product_units,
    product_formats,
    products
)

api_router = APIRouter()

# Include routers from endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(product_units.router, prefix="/product-units", tags=["product-units"])
api_router.include_router(product_formats.router, prefix="/product-formats", tags=["product-formats"])
api_router.include_router(products.router, prefix="/products", tags=["products"])

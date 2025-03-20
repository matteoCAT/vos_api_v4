from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, users

api_router = APIRouter()

# Include routers from endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Add other routers as you develop them
# api_router.include_router(products.router, prefix="/products", tags=["products"])
# api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
# api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.product import ProductType
from app.schemas.product import Product as ProductSchema, ProductDetail, ProductCreate, ProductUpdate, ProductResponse
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.product import product_crud
from app.crud.product_unit import product_unit_crud
from app.crud.product_format import product_format_crud

router = APIRouter()


def enhance_product_with_unit_info(db: Session, product):
    """
    Enhance product object with unit and format name information for UI display
    """
    # Create a new dictionary with all product attributes
    enhanced_product = product.__dict__.copy()

    # Remove SQLAlchemy state attributes
    if "_sa_instance_state" in enhanced_product:
        del enhanced_product["_sa_instance_state"]

    # Add unit names and symbols by querying the database
    purchase_unit = product_unit_crud.get(db, id=product.purchase_unit_id)
    sales_unit = product_unit_crud.get(db, id=product.sales_unit_id)

    if purchase_unit:
        enhanced_product["purchase_unit_name"] = purchase_unit.name
        enhanced_product["purchase_unit_symbol"] = purchase_unit.symbol
    else:
        enhanced_product["purchase_unit_name"] = "Unknown"
        enhanced_product["purchase_unit_symbol"] = "?"

    if sales_unit:
        enhanced_product["sales_unit_name"] = sales_unit.name
        enhanced_product["sales_unit_symbol"] = sales_unit.symbol
    else:
        enhanced_product["sales_unit_name"] = "Unknown"
        enhanced_product["sales_unit_symbol"] = "?"

    # Add format name if default_format_id exists
    if product.default_format_id:
        default_format = product_format_crud.get(db, id=product.default_format_id)
        if default_format:
            enhanced_product["default_format_name"] = default_format.name
        else:
            enhanced_product["default_format_name"] = None
    else:
        enhanced_product["default_format_name"] = None

    return enhanced_product


@router.get("/", response_model=List[ProductResponse], summary="Get all products")
def get_products(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = Query(None, description="Search query"),
        product_type: Optional[ProductType] = Query(None, description="Filter by product type"),
        active_only: bool = Query(False, description="Return only active products"),
        purchasable: Optional[bool] = Query(None, description="Filter by purchasable status"),
        sellable: Optional[bool] = Query(None, description="Filter by sellable status"),
        current_user: User = Depends(check_user_permissions(["view_products"]))
):
    """
    Retrieve all products with optional filtering.

    - **skip**: Number of products to skip (pagination)
    - **limit**: Maximum number of products to return (pagination)
    - **search**: Search query (searches name, code, description)
    - **product_type**: Filter by product type (unit, case, weight)
    - **active_only**: Return only active products
    - **purchasable**: Filter by purchasable status
    - **sellable**: Filter by sellable status
    """
    # Get products based on filters
    if search:
        products = product_crud.search(db, query=search, skip=skip, limit=limit)
    elif product_type:
        products = product_crud.get_by_type(db, product_type=product_type, skip=skip, limit=limit)
    elif active_only:
        products = product_crud.get_active(db, skip=skip, limit=limit)
    elif purchasable is not None and purchasable:
        products = product_crud.get_purchasable(db, skip=skip, limit=limit)
    elif sellable is not None and sellable:
        products = product_crud.get_sellable(db, skip=skip, limit=limit)
    else:
        products = product_crud.get_multi(db, skip=skip, limit=limit)

    # Enhance each product with unit and format names
    enhanced_products = [enhance_product_with_unit_info(db, product) for product in products]
    return enhanced_products


@router.post("/", response_model=ProductDetail, summary="Create new product")
def create_product(
        *,
        db: Session = Depends(get_db),
        product_in: ProductCreate,
        current_user: User = Depends(check_user_permissions(["create_products"]))
):
    """
    Create a new product.

    - Requires create_products permission
    """
    # Check if product with this code already exists
    if product_in.code:
        existing_product = product_crud.get_by_code(db, code=product_in.code)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="A product with this code already exists"
            )

    # Check if purchase unit exists
    purchase_unit = product_unit_crud.get(db, id=product_in.purchase_unit_id)
    if not purchase_unit:
        raise HTTPException(
            status_code=404,
            detail="Purchase unit not found"
        )
    if not purchase_unit.purchasable:
        raise HTTPException(
            status_code=400,
            detail="Selected purchase unit is not marked as purchasable"
        )

    # Check if sales unit exists
    sales_unit = product_unit_crud.get(db, id=product_in.sales_unit_id)
    if not sales_unit:
        raise HTTPException(
            status_code=404,
            detail="Sales unit not found"
        )
    if not sales_unit.sellable:
        raise HTTPException(
            status_code=400,
            detail="Selected sales unit is not marked as sellable"
        )

    # Check if default format exists (if provided)
    if product_in.default_format_id:
        default_format = product_format_crud.get(db, id=product_in.default_format_id)
        if not default_format:
            raise HTTPException(
                status_code=404,
                detail="Default format not found"
            )

    # Create new product
    product = product_crud.create(db, obj_in=product_in)
    return product


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
def get_product(
        *,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to get"),
        current_user: User = Depends(check_user_permissions(["view_products"]))
):
    """
    Get a specific product by ID.

    - Requires view_products permission
    """
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Enhance product with unit and format names for UI display
    enhanced_product = enhance_product_with_unit_info(db, product)
    return enhanced_product


@router.put("/{product_id}", response_model=ProductResponse, summary="Update product")
def update_product(
        *,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to update"),
        product_in: ProductUpdate,
        current_user: User = Depends(check_user_permissions(["update_products"]))
):
    """
    Update a product.

    - Requires update_products permission
    """
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Check for code uniqueness if updating code
    if product_in.code and product_in.code != product.code:
        existing_product = product_crud.get_by_code(db, code=product_in.code)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="A product with this code already exists"
            )

    # Check if purchase unit exists
    if product_in.purchase_unit_id:
        purchase_unit = product_unit_crud.get(db, id=product_in.purchase_unit_id)
        if not purchase_unit:
            raise HTTPException(
                status_code=404,
                detail="Purchase unit not found"
            )
        if not purchase_unit.purchasable:
            raise HTTPException(
                status_code=400,
                detail="Selected purchase unit is not marked as purchasable"
            )

    # Check if sales unit exists
    if product_in.sales_unit_id:
        sales_unit = product_unit_crud.get(db, id=product_in.sales_unit_id)
        if not sales_unit:
            raise HTTPException(
                status_code=404,
                detail="Sales unit not found"
            )
        if not sales_unit.sellable:
            raise HTTPException(
                status_code=400,
                detail="Selected sales unit is not marked as sellable"
            )

    # Check if default format exists
    if product_in.default_format_id:
        default_format = product_format_crud.get(db, id=product_in.default_format_id)
        if not default_format:
            raise HTTPException(
                status_code=404,
                detail="Default format not found"
            )

    # Update product
    product = product_crud.update(db, db_obj=product, obj_in=product_in)

    # Enhance product with unit and format names
    enhanced_product = enhance_product_with_unit_info(db, product)
    return enhanced_product


@router.delete("/{product_id}", response_model=ProductResponse, summary="Delete product")
def delete_product(
        *,
        db: Session = Depends(get_db),
        product_id: UUID = Path(..., description="The ID of the product to delete"),
        current_user: User = Depends(check_user_permissions(["delete_products"]))
):
    """
    Delete a product.

    - Requires delete_products permission
    """
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # In a more complete implementation, we would check if this product is referenced
    # by any orders, recipes, etc., and prevent deletion if needed

    # Save product info before deletion for response
    enhanced_product = enhance_product_with_unit_info(db, product)

    # Remove the product
    product_crud.remove(db, id=product_id)

    return enhanced_product


@router.get("/by-code/{code}", response_model=ProductResponse, summary="Get product by code")
def get_product_by_code(
        *,
        db: Session = Depends(get_db),
        code: str = Path(..., description="The code of the product to get"),
        current_user: User = Depends(check_user_permissions(["view_products"]))
):
    """
    Get a specific product by code.

    - Requires view_products permission
    """
    product = product_crud.get_by_code(db, code=code)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Enhance product with unit and format names for UI display
    enhanced_product = enhance_product_with_unit_info(db, product)
    return enhanced_product
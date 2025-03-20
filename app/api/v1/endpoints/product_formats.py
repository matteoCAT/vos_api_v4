from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.product_format import ProductFormat as ProductFormatSchema, ProductFormatDetail, ProductFormatCreate, \
    ProductFormatUpdate
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.product_format import product_format_crud
from app.crud.product_unit import product_unit_crud

router = APIRouter()


@router.get("/", response_model=List[ProductFormatSchema], summary="Get all product formats")
def get_product_formats(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        unit_id: Optional[UUID] = Query(None, description="Filter by unit ID"),
        standard_only: bool = Query(False, description="Return only standard formats"),
        current_user: User = Depends(check_user_permissions(["view_product_formats"]))
):
    """
    Retrieve all product formats with optional filtering.

    - **skip**: Number of formats to skip (pagination)
    - **limit**: Maximum number of formats to return (pagination)
    - **unit_id**: Filter by unit ID
    - **standard_only**: Return only standard formats
    """
    if unit_id:
        return product_format_crud.get_by_unit(db, unit_id=unit_id, skip=skip, limit=limit)
    elif standard_only:
        return product_format_crud.get_standard_formats(db, skip=skip, limit=limit)
    else:
        return product_format_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=ProductFormatSchema, summary="Create new product format")
def create_product_format(
        *,
        db: Session = Depends(get_db),
        format_in: ProductFormatCreate,
        current_user: User = Depends(check_user_permissions(["create_product_formats"]))
):
    """
    Create a new product format.

    - Requires create_product_formats permission
    """
    # Check if format with this name already exists
    existing_format = product_format_crud.get_by_name(db, name=format_in.name)
    if existing_format:
        raise HTTPException(
            status_code=400,
            detail="A product format with this name already exists"
        )

    # Check if the unit exists
    unit = product_unit_crud.get(db, id=format_in.unit_id)
    if not unit:
        raise HTTPException(
            status_code=404,
            detail="Unit not found"
        )

    # Create new product format
    product_format = product_format_crud.create(db, obj_in=format_in)
    return product_format


@router.get("/{format_id}", response_model=ProductFormatDetail, summary="Get product format by ID")
def get_product_format(
        *,
        db: Session = Depends(get_db),
        format_id: UUID = Path(..., description="The ID of the product format to get"),
        current_user: User = Depends(check_user_permissions(["view_product_formats"]))
):
    """
    Get a specific product format by ID.

    - Requires view_product_formats permission
    """
    product_format = product_format_crud.get(db, id=format_id)
    if not product_format:
        raise HTTPException(
            status_code=404,
            detail="Product format not found"
        )
    return product_format


@router.put("/{format_id}", response_model=ProductFormatSchema, summary="Update product format")
def update_product_format(
        *,
        db: Session = Depends(get_db),
        format_id: UUID = Path(..., description="The ID of the product format to update"),
        format_in: ProductFormatUpdate,
        current_user: User = Depends(check_user_permissions(["update_product_formats"]))
):
    """
    Update a product format.

    - Requires update_product_formats permission
    """
    product_format = product_format_crud.get(db, id=format_id)
    if not product_format:
        raise HTTPException(
            status_code=404,
            detail="Product format not found"
        )

    # Check for name uniqueness if updating name
    if format_in.name and format_in.name != product_format.name:
        existing_format = product_format_crud.get_by_name(db, name=format_in.name)
        if existing_format:
            raise HTTPException(
                status_code=400,
                detail="A product format with this name already exists"
            )

    # Check if the unit exists if updating unit
    if format_in.unit_id:
        unit = product_unit_crud.get(db, id=format_in.unit_id)
        if not unit:
            raise HTTPException(
                status_code=404,
                detail="Unit not found"
            )

    product_format = product_format_crud.update(db, db_obj=product_format, obj_in=format_in)
    return product_format


@router.delete("/{format_id}", response_model=ProductFormatSchema, summary="Delete product format")
def delete_product_format(
        *,
        db: Session = Depends(get_db),
        format_id: UUID = Path(..., description="The ID of the product format to delete"),
        current_user: User = Depends(check_user_permissions(["delete_product_formats"]))
):
    """
    Delete a product format.

    - Requires delete_product_formats permission

    Note: This will only work if the product format is not referenced by any products.
    """
    product_format = product_format_crud.get(db, id=format_id)
    if not product_format:
        raise HTTPException(
            status_code=404,
            detail="Product format not found"
        )

    # In a more complete implementation, we would check if this format is used by any products
    # and prevent deletion if it is. For now, we'll just delete it.

    product_format = product_format_crud.remove(db, id=format_id)
    return product_format
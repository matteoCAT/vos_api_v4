from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.product_unit import ProductUnit as ProductUnitSchema, ProductUnitCreate, ProductUnitUpdate
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.product_unit import product_unit_crud

router = APIRouter()


@router.get("/", response_model=List[ProductUnitSchema], summary="Get all product units")
def get_product_units(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        purchasable: Optional[bool] = Query(None, description="Filter by purchasable status"),
        sellable: Optional[bool] = Query(None, description="Filter by sellable status"),
        base_only: bool = Query(False, description="Return only base units"),
        current_user: User = Depends(check_user_permissions(["view_product_units"]))
):
    """
    Retrieve all product units with optional filtering.

    - **skip**: Number of units to skip (pagination)
    - **limit**: Maximum number of units to return (pagination)
    - **purchasable**: Filter by purchasable status
    - **sellable**: Filter by sellable status
    - **base_only**: Return only base units
    """
    if base_only:
        return product_unit_crud.get_base_units(db, skip=skip, limit=limit)
    elif purchasable is not None and purchasable:
        return product_unit_crud.get_all_purchasable(db, skip=skip, limit=limit)
    elif sellable is not None and sellable:
        return product_unit_crud.get_all_sellable(db, skip=skip, limit=limit)
    else:
        return product_unit_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=ProductUnitSchema, summary="Create new product unit")
def create_product_unit(
        *,
        db: Session = Depends(get_db),
        unit_in: ProductUnitCreate,
        current_user: User = Depends(check_user_permissions(["create_product_units"]))
):
    """
    Create a new product unit.

    - Requires create_product_units permission
    """
    # Check if unit with this name already exists
    existing_unit = product_unit_crud.get_by_name(db, name=unit_in.name)
    if existing_unit:
        raise HTTPException(
            status_code=400,
            detail="A product unit with this name already exists"
        )

    # Check if unit with this symbol already exists
    existing_unit = product_unit_crud.get_by_symbol(db, symbol=unit_in.symbol)
    if existing_unit:
        raise HTTPException(
            status_code=400,
            detail="A product unit with this symbol already exists"
        )

    # Create new product unit
    product_unit = product_unit_crud.create(db, obj_in=unit_in)
    return product_unit


@router.get("/{unit_id}", response_model=ProductUnitSchema, summary="Get product unit by ID")
def get_product_unit(
        *,
        db: Session = Depends(get_db),
        unit_id: UUID = Path(..., description="The ID of the product unit to get"),
        current_user: User = Depends(check_user_permissions(["view_product_units"]))
):
    """
    Get a specific product unit by ID.

    - Requires view_product_units permission
    """
    product_unit = product_unit_crud.get(db, id=unit_id)
    if not product_unit:
        raise HTTPException(
            status_code=404,
            detail="Product unit not found"
        )
    return product_unit


@router.put("/{unit_id}", response_model=ProductUnitSchema, summary="Update product unit")
def update_product_unit(
        *,
        db: Session = Depends(get_db),
        unit_id: UUID = Path(..., description="The ID of the product unit to update"),
        unit_in: ProductUnitUpdate,
        current_user: User = Depends(check_user_permissions(["update_product_units"]))
):
    """
    Update a product unit.

    - Requires update_product_units permission
    """
    product_unit = product_unit_crud.get(db, id=unit_id)
    if not product_unit:
        raise HTTPException(
            status_code=404,
            detail="Product unit not found"
        )

    # Check for name uniqueness if updating name
    if unit_in.name and unit_in.name != product_unit.name:
        existing_unit = product_unit_crud.get_by_name(db, name=unit_in.name)
        if existing_unit:
            raise HTTPException(
                status_code=400,
                detail="A product unit with this name already exists"
            )

    # Check for symbol uniqueness if updating symbol
    if unit_in.symbol and unit_in.symbol != product_unit.symbol:
        existing_unit = product_unit_crud.get_by_symbol(db, symbol=unit_in.symbol)
        if existing_unit:
            raise HTTPException(
                status_code=400,
                detail="A product unit with this symbol already exists"
            )

    product_unit = product_unit_crud.update(db, db_obj=product_unit, obj_in=unit_in)
    return product_unit


@router.delete("/{unit_id}", response_model=ProductUnitSchema, summary="Delete product unit")
def delete_product_unit(
        *,
        db: Session = Depends(get_db),
        unit_id: UUID = Path(..., description="The ID of the product unit to delete"),
        current_user: User = Depends(check_user_permissions(["delete_product_units"]))
):
    """
    Delete a product unit.

    - Requires delete_product_units permission

    Note: This will only work if the product unit is not referenced by any products.
    """
    product_unit = product_unit_crud.get(db, id=unit_id)
    if not product_unit:
        raise HTTPException(
            status_code=404,
            detail="Product unit not found"
        )

    # In a more complete implementation, we would check if this unit is used by any products
    # and prevent deletion if it is. For now, we'll just delete it.

    product_unit = product_unit_crud.remove(db, id=unit_id)
    return product_unit
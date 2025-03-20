from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.supplier import Supplier
from app.schemas.supplier import Supplier as SupplierSchema, SupplierCreate, SupplierUpdate
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.supplier import supplier as supplier_crud

router = APIRouter()


@router.get("/", response_model=List[SupplierSchema], summary="Get all suppliers")
def get_suppliers(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        current_user: User = Depends(check_user_permissions(["view_suppliers"]))
):
    """
    Retrieve all suppliers.

    - **skip**: Number of suppliers to skip
    - **limit**: Maximum number of suppliers to return
    - **active_only**: If true, only return active suppliers
    """
    if active_only:
        suppliers = supplier_crud.get_active(db, skip=skip, limit=limit)
    else:
        suppliers = supplier_crud.get_multi(db, skip=skip, limit=limit)
    return suppliers


@router.post("/", response_model=SupplierSchema, summary="Create new supplier")
def create_supplier(
        *,
        db: Session = Depends(get_db),
        supplier_in: SupplierCreate,
        current_user: User = Depends(check_user_permissions(["create_suppliers"]))
):
    """
    Create a new supplier.
    """
    # Check if supplier with same tax_id already exists (if provided)
    if supplier_in.tax_id:
        supplier = supplier_crud.get_by_tax_id(db, tax_id=supplier_in.tax_id)
        if supplier:
            raise HTTPException(
                status_code=400,
                detail="A supplier with this tax ID already exists."
            )

    # Create new supplier
    supplier = supplier_crud.create(db, obj_in=supplier_in)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierSchema, summary="Get supplier by ID")
def get_supplier(
        *,
        db: Session = Depends(get_db),
        supplier_id: UUID = Path(..., description="The ID of the supplier to get"),
        current_user: User = Depends(check_user_permissions(["view_suppliers"]))
):
    """
    Get a specific supplier by ID.
    """
    supplier = supplier_crud.get(db, id=supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )
    return supplier


@router.put("/{supplier_id}", response_model=SupplierSchema, summary="Update supplier")
def update_supplier(
        *,
        db: Session = Depends(get_db),
        supplier_id: UUID = Path(..., description="The ID of the supplier to update"),
        supplier_in: SupplierUpdate,
        current_user: User = Depends(check_user_permissions(["update_suppliers"]))
):
    """
    Update a supplier.
    """
    supplier = supplier_crud.get(db, id=supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    # Prevent tax_id duplicates if updating tax_id
    if supplier_in.tax_id and supplier_in.tax_id != supplier.tax_id:
        existing_supplier = supplier_crud.get_by_tax_id(db, tax_id=supplier_in.tax_id)
        if existing_supplier:
            raise HTTPException(
                status_code=400,
                detail="A supplier with this tax ID already exists."
            )

    supplier = supplier_crud.update(db, db_obj=supplier, obj_in=supplier_in)
    return supplier


@router.delete("/{supplier_id}", response_model=SupplierSchema, summary="Delete supplier")
def delete_supplier(
        *,
        db: Session = Depends(get_db),
        supplier_id: UUID = Path(..., description="The ID of the supplier to delete"),
        current_user: User = Depends(check_user_permissions(["delete_suppliers"]))
):
    """
    Delete a supplier.
    """
    supplier = supplier_crud.get(db, id=supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    supplier = supplier_crud.remove(db, id=supplier_id)
    return supplier


@router.patch("/{supplier_id}/activate", response_model=SupplierSchema, summary="Activate supplier")
def activate_supplier(
        *,
        db: Session = Depends(get_db),
        supplier_id: UUID = Path(..., description="The ID of the supplier to activate"),
        current_user: User = Depends(check_user_permissions(["update_suppliers"]))
):
    """
    Activate a supplier.
    """
    supplier = supplier_crud.get(db, id=supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    supplier_in = {"is_active": True}
    supplier = supplier_crud.update(db, db_obj=supplier, obj_in=supplier_in)
    return supplier


@router.patch("/{supplier_id}/deactivate", response_model=SupplierSchema, summary="Deactivate supplier")
def deactivate_supplier(
        *,
        db: Session = Depends(get_db),
        supplier_id: UUID = Path(..., description="The ID of the supplier to deactivate"),
        current_user: User = Depends(check_user_permissions(["update_suppliers"]))
):
    """
    Deactivate a supplier.
    """
    supplier = supplier_crud.get(db, id=supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    supplier_in = {"is_active": False}
    supplier = supplier_crud.update(db, db_obj=supplier, obj_in=supplier_in)
    return supplier
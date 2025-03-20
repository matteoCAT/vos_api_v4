from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from uuid import UUID

from app.models.user import User
from app.models.invoice import PaymentStatus, InvoiceItem
from app.schemas.invoice import (
    Invoice as InvoiceSchema,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceDetail,
    InvoiceItem as InvoiceItemSchema,
    InvoiceItemCreate,
    InvoiceItemUpdate,
    InvoiceItemDetail
)
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.invoice import invoice_crud
from app.crud.product import product_crud
from app.crud.product_unit import product_unit_crud

router = APIRouter()


def enhance_invoice_item(db: Session, item: InvoiceItem) -> Dict[str, Any]:
    """
    Enhance invoice item with product and unit information
    """
    enhanced_item = item.__dict__.copy()

    # Remove SQLAlchemy state attributes
    if "_sa_instance_state" in enhanced_item:
        del enhanced_item["_sa_instance_state"]

    # Add product name if product exists
    product = product_crud.get(db, id=item.product_id)
    if product:
        enhanced_item["product_name"] = product.name
    else:
        enhanced_item["product_name"] = "Unknown Product"

    # Add unit information if unit exists
    unit = product_unit_crud.get(db, id=item.unit_id)
    if unit:
        enhanced_item["unit_name"] = unit.name
        enhanced_item["unit_symbol"] = unit.symbol
    else:
        enhanced_item["unit_name"] = "Unknown Unit"
        enhanced_item["unit_symbol"] = "?"

    return enhanced_item


def enhance_invoice_with_details(db: Session, invoice):
    """
    Enhance invoice with supplier details and enhanced items
    """
    # Start with a copy of the invoice's attributes
    enhanced_invoice = invoice.__dict__.copy()

    # Remove SQLAlchemy state attributes
    if "_sa_instance_state" in enhanced_invoice:
        del enhanced_invoice["_sa_instance_state"]

    # Add supplier details
    if hasattr(invoice, "supplier") and invoice.supplier:
        enhanced_invoice["supplier"] = invoice.supplier

    # Enhance each item
    enhanced_items = []
    for item in invoice.items:
        enhanced_items.append(enhance_invoice_item(db, item))

    enhanced_invoice["items"] = enhanced_items

    return enhanced_invoice


@router.get("/", response_model=List[InvoiceSchema], summary="Get all invoices")
def get_invoices(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        supplier_id: Optional[UUID] = Query(None, description="Filter by supplier ID"),
        status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
        start_date: Optional[date] = Query(None, description="Filter by start date"),
        end_date: Optional[date] = Query(None, description="Filter by end date"),
        overdue: bool = Query(False, description="Filter for overdue invoices"),
        due_this_week: bool = Query(False, description="Filter for invoices due this week"),
        current_user: User = Depends(check_user_permissions(["view_invoices"]))
):
    """
    Retrieve all invoices with optional filtering.

    - **skip**: Number of invoices to skip (pagination)
    - **limit**: Maximum number of invoices to return (pagination)
    - **supplier_id**: Filter by supplier
    - **status**: Filter by payment status
    - **start_date**: Filter by invoice date from
    - **end_date**: Filter by invoice date to
    - **overdue**: Filter for overdue invoices
    - **due_this_week**: Filter for invoices due this week
    """
    if supplier_id:
        return invoice_crud.get_by_supplier(db, supplier_id=supplier_id, skip=skip, limit=limit)
    elif status:
        return invoice_crud.get_by_payment_status(db, status=status, skip=skip, limit=limit)
    elif start_date and end_date:
        return invoice_crud.get_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    elif overdue:
        return invoice_crud.get_overdue(db, skip=skip, limit=limit)
    elif due_this_week:
        return invoice_crud.get_due_this_week(db, skip=skip, limit=limit)
    else:
        return invoice_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=InvoiceDetail, status_code=status.HTTP_201_CREATED, summary="Create new invoice")
def create_invoice(
        *,
        db: Session = Depends(get_db),
        invoice_in: InvoiceCreate,
        current_user: User = Depends(check_user_permissions(["create_invoices"]))
):
    """
    Create a new invoice with items.

    - Requires create_invoices permission
    """
    # Check if invoice with this number already exists
    existing_invoice = invoice_crud.get_by_invoice_number(db, invoice_number=invoice_in.invoice_number)
    if existing_invoice:
        raise HTTPException(
            status_code=400,
            detail="An invoice with this number already exists"
        )

    # Fetch all products needed for the invoice items
    product_ids = [item.product_id for item in invoice_in.items]
    products_db = product_crud.get_multi_by_ids(db, ids=product_ids) if product_ids else []
    products = {str(p.id): p for p in products_db}

    # Create the invoice with items
    invoice = invoice_crud.create_with_items(db=db, obj_in=invoice_in, products=products)

    # Enhance invoice with details for response
    enhanced_invoice = enhance_invoice_with_details(db, invoice)
    return enhanced_invoice


@router.get("/{invoice_id}", response_model=InvoiceDetail, summary="Get invoice by ID")
def get_invoice(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice to get"),
        current_user: User = Depends(check_user_permissions(["view_invoices"]))
):
    """
    Get a specific invoice by ID with all its items.

    - Requires view_invoices permission
    """
    invoice = invoice_crud.get_with_items(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Enhance invoice with details for response
    enhanced_invoice = enhance_invoice_with_details(db, invoice)
    return enhanced_invoice


@router.put("/{invoice_id}", response_model=InvoiceDetail, summary="Update invoice")
def update_invoice(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice to update"),
        invoice_in: InvoiceUpdate,
        current_user: User = Depends(check_user_permissions(["update_invoices"]))
):
    """
    Update an invoice.

    - Requires update_invoices permission

    Note: This endpoint only updates the invoice header. Use the items endpoints to update invoice items.
    """
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Check for invoice number uniqueness if updating
    if invoice_in.invoice_number and invoice_in.invoice_number != invoice.invoice_number:
        existing_invoice = invoice_crud.get_by_invoice_number(db, invoice_number=invoice_in.invoice_number)
        if existing_invoice:
            raise HTTPException(
                status_code=400,
                detail="An invoice with this number already exists"
            )

    # Update invoice
    invoice = invoice_crud.update(db, db_obj=invoice, obj_in=invoice_in)

    # Refresh to get updated items
    invoice = invoice_crud.get_with_items(db, id=invoice_id)

    # Enhance invoice with details for response
    enhanced_invoice = enhance_invoice_with_details(db, invoice)
    return enhanced_invoice


@router.delete("/{invoice_id}", response_model=InvoiceSchema, summary="Delete invoice")
def delete_invoice(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice to delete"),
        current_user: User = Depends(check_user_permissions(["delete_invoices"]))
):
    """
    Delete an invoice.

    - Requires delete_invoices permission

    Note: This will also delete all items of this invoice.
    """
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Delete the invoice (cascade delete will handle items)
    invoice = invoice_crud.remove(db, id=invoice_id)
    return invoice


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceSchema, summary="Mark invoice as paid")
def mark_invoice_as_paid(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice to mark as paid"),
        payment_date: Optional[date] = Body(None, description="Payment date"),
        payment_reference: Optional[str] = Body(None, description="Payment reference"),
        current_user: User = Depends(check_user_permissions(["update_invoices"]))
):
    """
    Mark an invoice as paid.

    - Requires update_invoices permission
    """
    invoice = invoice_crud.mark_as_paid(
        db=db,
        invoice_id=invoice_id,
        payment_date=payment_date,
        payment_reference=payment_reference
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    return invoice


# Invoice Items Endpoints

@router.get("/{invoice_id}/items", response_model=List[InvoiceItemDetail], summary="Get invoice items")
def get_invoice_items(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice"),
        current_user: User = Depends(check_user_permissions(["view_invoices"]))
):
    """
    Get all items for a specific invoice.

    - Requires view_invoices permission
    """
    invoice = invoice_crud.get_with_items(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Enhance items with details
    enhanced_items = [enhance_invoice_item(db, item) for item in invoice.items]
    return enhanced_items


@router.post("/{invoice_id}/items", response_model=InvoiceItemDetail, status_code=status.HTTP_201_CREATED,
             summary="Add invoice item")
def add_invoice_item(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice"),
        item_in: InvoiceItemCreate,
        current_user: User = Depends(check_user_permissions(["update_invoices"]))
):
    """
    Add a new item to an invoice.

    - Requires update_invoices permission
    """
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Get the product
    product = product_crud.get(db, id=item_in.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Add the item
    update_items = []
    new_items = [(item_in, product)]
    delete_item_ids = []

    invoice = invoice_crud.update_with_items(
        db=db,
        db_obj=invoice,
        obj_in={},  # No changes to invoice header
        update_items=update_items,
        new_items=new_items,
        delete_item_ids=delete_item_ids
    )

    # Get the newly added item (last item added)
    new_item = invoice.items[-1] if invoice.items else None
    if not new_item:
        raise HTTPException(
            status_code=500,
            detail="Failed to add item to invoice"
        )

    # Enhance item with details
    enhanced_item = enhance_invoice_item(db, new_item)
    return enhanced_item


@router.put("/{invoice_id}/items/{item_id}", response_model=InvoiceItemDetail, summary="Update invoice item")
def update_invoice_item(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice"),
        item_id: UUID = Path(..., description="The ID of the item to update"),
        item_in: InvoiceItemUpdate,
        current_user: User = Depends(check_user_permissions(["update_invoices"]))
):
    """
    Update an invoice item.

    - Requires update_invoices permission
    """
    # Check if invoice exists
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Check if item exists and belongs to the invoice
    item = db.query(InvoiceItem).filter(
        InvoiceItem.id == item_id,
        InvoiceItem.invoice_id == invoice_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Invoice item not found or doesn't belong to this invoice"
        )

    # Update the product reference if changed
    if item_in.product_id and item_in.product_id != item.product_id:
        product = product_crud.get(db, id=item_in.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

    # Update the item
    update_items = [(item, item_in)]

    invoice = invoice_crud.update_with_items(
        db=db,
        db_obj=invoice,
        obj_in={},  # No changes to invoice header
        update_items=update_items,
        new_items=[],
        delete_item_ids=[]
    )

    # Find the updated item
    updated_item = next((i for i in invoice.items if str(i.id) == str(item_id)), None)
    if not updated_item:
        raise HTTPException(
            status_code=500,
            detail="Failed to update invoice item"
        )

    # Enhance item with details
    enhanced_item = enhance_invoice_item(db, updated_item)
    return enhanced_item


@router.delete("/{invoice_id}/items/{item_id}", response_model=InvoiceSchema, summary="Delete invoice item")
def delete_invoice_item(
        *,
        db: Session = Depends(get_db),
        invoice_id: UUID = Path(..., description="The ID of the invoice"),
        item_id: UUID = Path(..., description="The ID of the item to delete"),
        current_user: User = Depends(check_user_permissions(["update_invoices"]))
):
    """
    Delete an invoice item.

    - Requires update_invoices permission
    """
    # Check if invoice exists
    invoice = invoice_crud.get(db, id=invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # Check if item exists and belongs to the invoice
    item = db.query(InvoiceItem).filter(
        InvoiceItem.id == item_id,
        InvoiceItem.invoice_id == invoice_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Invoice item not found or doesn't belong to this invoice"
        )

    # Delete the item and update invoice totals
    invoice = invoice_crud.update_with_items(
        db=db,
        db_obj=invoice,
        obj_in={},  # No changes to invoice header
        update_items=[],
        new_items=[],
        delete_item_ids=[item_id]
    )

    return invoice
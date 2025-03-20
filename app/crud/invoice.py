from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models.invoice import Invoice, InvoiceItem, PaymentStatus
from app.models.product import Product
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceItemCreate, InvoiceItemUpdate


class CRUDInvoiceItem(CRUDBase[InvoiceItem, InvoiceItemCreate, InvoiceItemUpdate]):
    """
    CRUD operations for InvoiceItem model
    """

    def create_with_invoice(
            self, db: Session, *, obj_in: InvoiceItemCreate, invoice_id: Any, product: Product
    ) -> InvoiceItem:
        """
        Create a new invoice item with automatic calculations

        Args:
            db: Database session
            obj_in: InvoiceItemCreate schema
            invoice_id: ID of the parent invoice
            product: Product instance for the item

        Returns:
            InvoiceItem: Created invoice item
        """
        # Create dict with invoice_id and item data
        obj_in_data = obj_in.dict()
        obj_in_data["invoice_id"] = invoice_id

        # Use product description if not provided
        if not obj_in_data.get("description"):
            obj_in_data["description"] = product.name

        # Use product VAT rate if not provided
        if not obj_in_data.get("vat_rate") and hasattr(product, "vat_rate"):
            obj_in_data["vat_rate"] = float(product.vat_rate)

        # Create the invoice item
        db_obj = InvoiceItem(**obj_in_data)

        # Calculate amounts
        db_obj.calculate_amounts()

        # Add to session and return
        db.add(db_obj)
        db.flush()  # Flush to get the ID but don't commit yet
        return db_obj

    def update_with_calculations(
            self, db: Session, *, db_obj: InvoiceItem, obj_in: Union[InvoiceItemUpdate, Dict[str, Any]]
    ) -> InvoiceItem:
        """
        Update an invoice item and recalculate amounts

        Args:
            db: Database session
            db_obj: InvoiceItem model instance
            obj_in: InvoiceItemUpdate schema or dict

        Returns:
            InvoiceItem: Updated invoice item
        """
        # First, update the invoice item
        updated_item = super().update(db, db_obj=db_obj, obj_in=obj_in)

        # Recalculate amounts
        updated_item.calculate_amounts()

        # Add to session but don't commit yet
        db.add(updated_item)
        db.flush()

        return updated_item


class CRUDInvoice(CRUDBase[Invoice, InvoiceCreate, InvoiceUpdate]):
    """
    CRUD operations for Invoice model
    """

    def __init__(self):
        super().__init__(Invoice)
        self.item_crud = CRUDInvoiceItem(InvoiceItem)

    def get_by_invoice_number(self, db: Session, *, invoice_number: str) -> Optional[Invoice]:
        """
        Get an invoice by invoice number

        Args:
            db: Database session
            invoice_number: Invoice number

        Returns:
            Optional[Invoice]: Invoice instance if found, None otherwise
        """
        return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

    def get_by_supplier(
            self, db: Session, *, supplier_id: Any, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """
        Get all invoices for a specific supplier

        Args:
            db: Database session
            supplier_id: Supplier ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Invoice]: List of invoices for the supplier
        """
        return (
            db.query(Invoice)
            .filter(Invoice.supplier_id == supplier_id)
            .order_by(Invoice.invoice_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_payment_status(
            self, db: Session, *, status: PaymentStatus, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """
        Get all invoices with a specific payment status

        Args:
            db: Database session
            status: Payment status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Invoice]: List of invoices with the payment status
        """
        return (
            db.query(Invoice)
            .filter(Invoice.payment_status == status)
            .order_by(Invoice.due_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_overdue(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """
        Get all overdue invoices

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Invoice]: List of overdue invoices
        """
        today = date.today()
        return (
            db.query(Invoice)
            .filter(
                and_(
                    Invoice.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL]),
                    Invoice.due_date < today
                )
            )
            .order_by(Invoice.due_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
            self, db: Session, *, start_date: date, end_date: date, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """
        Get all invoices within a date range

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Invoice]: List of invoices in the date range
        """
        return (
            db.query(Invoice)
            .filter(
                and_(
                    Invoice.invoice_date >= start_date,
                    Invoice.invoice_date <= end_date
                )
            )
            .order_by(Invoice.invoice_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_due_this_week(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """
        Get all invoices due this week

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Invoice]: List of invoices due this week
        """
        today = date.today()
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        return (
            db.query(Invoice)
            .filter(
                and_(
                    Invoice.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL]),
                    Invoice.due_date >= today,
                    Invoice.due_date <= end_of_week
                )
            )
            .order_by(Invoice.due_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_items(self, db: Session, *, id: Any) -> Optional[Invoice]:
        """
        Get an invoice with all its items

        Args:
            db: Database session
            id: Invoice ID

        Returns:
            Optional[Invoice]: Invoice instance with items if found, None otherwise
        """
        return db.query(Invoice).filter(Invoice.id == id).first()

    def create_with_items(
            self, db: Session, *, obj_in: InvoiceCreate, products: Dict[Any, Product]
    ) -> Invoice:
        """
        Create a new invoice with items

        Args:
            db: Database session
            obj_in: InvoiceCreate schema
            products: Dictionary of products keyed by product_id

        Returns:
            Invoice: Created invoice
        """
        # Create the invoice first without items
        obj_in_data = obj_in.dict(exclude={"items"})
        db_obj = Invoice(**obj_in_data)
        db.add(db_obj)
        db.flush()  # Flush to get the ID but don't commit yet

        # Add items if any
        for item_data in obj_in.items:
            product = products.get(item_data.product_id)
            if not product:
                continue  # Skip if product not found

            self.item_crud.create_with_invoice(
                db=db, obj_in=item_data, invoice_id=db_obj.id, product=product
            )

        # Update invoice totals
        db_obj.update_totals()

        # Commit changes
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update_with_items(
            self,
            db: Session,
            *,
            db_obj: Invoice,
            obj_in: Union[InvoiceUpdate, Dict[str, Any]],
            update_items: Optional[List[Tuple[InvoiceItem, InvoiceItemUpdate]]] = None,
            new_items: Optional[List[Tuple[InvoiceItemCreate, Product]]] = None,
            delete_item_ids: Optional[List[Any]] = None
    ) -> Invoice:
        """
        Update an invoice and its items

        Args:
            db: Database session
            db_obj: Invoice model instance
            obj_in: InvoiceUpdate schema or dict
            update_items: List of tuples (item_obj, item_update) for items to update
            new_items: List of tuples (item_create, product) for new items
            delete_item_ids: List of item IDs to delete

        Returns:
            Invoice: Updated invoice
        """
        # First, update the invoice
        updated_invoice = super().update(db, db_obj=db_obj, obj_in=obj_in)

        # Update existing items
        if update_items:
            for item_obj, item_update in update_items:
                self.item_crud.update_with_calculations(
                    db=db, db_obj=item_obj, obj_in=item_update
                )

        # Add new items
        if new_items:
            for item_create, product in new_items:
                self.item_crud.create_with_invoice(
                    db=db, obj_in=item_create, invoice_id=updated_invoice.id, product=product
                )

        # Delete items
        if delete_item_ids:
            for item_id in delete_item_ids:
                item = db.query(InvoiceItem).get(item_id)
                if item and item.invoice_id == updated_invoice.id:
                    db.delete(item)

        # Recalculate invoice totals
        db.flush()  # Make sure all item changes are visible
        updated_invoice.update_totals()

        # Commit changes
        db.add(updated_invoice)
        db.commit()
        db.refresh(updated_invoice)

        return updated_invoice

    def mark_as_paid(
            self, db: Session, *, invoice_id: Any, payment_date: date = None, payment_reference: str = None
    ) -> Optional[Invoice]:
        """
        Mark an invoice as paid

        Args:
            db: Database session
            invoice_id: Invoice ID
            payment_date: Payment date (defaults to today)
            payment_reference: Payment reference

        Returns:
            Optional[Invoice]: Updated invoice if found, None otherwise
        """
        invoice = self.get(db, id=invoice_id)
        if not invoice:
            return None

        # Update payment information
        update_data = {
            "payment_status": PaymentStatus.PAID,
            "payment_date": payment_date or date.today(),
        }

        if payment_reference:
            update_data["payment_reference"] = payment_reference

        return self.update(db, db_obj=invoice, obj_in=update_data)


invoice_crud = CRUDInvoice()
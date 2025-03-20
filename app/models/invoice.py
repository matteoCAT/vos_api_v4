from datetime import date, datetime
import enum
from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey, Enum, Boolean, Text, Numeric
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from decimal import Decimal

from app.models.base import BaseModel


class PaymentStatus(str, enum.Enum):
    """Enumeration of payment statuses"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(BaseModel):
    """
    Model for supplier invoices
    """
    # Invoice number (potentially from supplier)
    invoice_number = Column(String, index=True, nullable=False)

    # Invoice reference (internal reference)
    reference = Column(String, index=True, nullable=True)

    # Supplier information
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("supplier.id"), nullable=False)
    supplier = relationship("Supplier", backref="invoices")

    # Order and delivery tracking
    order_date = Column(Date, nullable=True, comment="Date when the order was placed")
    order_number = Column(String, nullable=True, comment="Order/PO number")
    delivery_date = Column(Date, nullable=True, comment="Date when goods were delivered")
    delivery_note = Column(String, nullable=True, comment="Delivery note reference")

    # Invoice dates
    invoice_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    received_date = Column(Date, nullable=True, comment="Date invoice was received")

    # Payment information
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_date = Column(Date, nullable=True, comment="Date payment was made")
    payment_reference = Column(String, nullable=True, comment="Payment reference/transaction ID")
    payment_method = Column(String, nullable=True, comment="Method of payment (e.g., bank transfer, check)")

    # Notes
    notes = Column(Text, nullable=True)

    # Totals (to avoid recalculating from items each time)
    subtotal = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    total_discount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    total_net = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    total_vat = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    total_gross = Column(Numeric(precision=10, scale=2), nullable=False, default=0)

    # Relationship to invoice items
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    @validates('due_date')
    def validate_due_date(self, key, due_date):
        """Validates that due_date is not before invoice_date"""
        if hasattr(self, 'invoice_date') and self.invoice_date and due_date < self.invoice_date:
            raise ValueError("Due date cannot be before invoice date")
        return due_date

    def update_totals(self):
        """Update invoice totals based on items"""
        # Convert all values to Decimal for consistent calculation
        self.subtotal = sum(Decimal(str(item.subtotal)) for item in self.items)
        self.total_discount = sum(item.discount_amount for item in self.items)
        self.total_net = sum(item.net_amount for item in self.items)
        self.total_vat = sum(item.vat_amount for item in self.items)
        self.total_gross = sum(item.gross_amount for item in self.items)

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.payment_status}>"


class InvoiceItem(BaseModel):
    """
    Model for line items in an invoice
    """
    # Relationship to the parent invoice
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id", ondelete="CASCADE"), nullable=False)
    invoice = relationship("Invoice", back_populates="items")

    # Product information
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False)
    product = relationship("Product")

    # Description (copied from product, but can be overridden)
    description = Column(String, nullable=True)

    # Quantity and units
    quantity = Column(Numeric(precision=10, scale=3), nullable=False)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("productunit.id"), nullable=False)
    unit = relationship("ProductUnit")

    # Pricing
    unit_price = Column(Numeric(precision=10, scale=2), nullable=False)
    discount_percentage = Column(Numeric(precision=5, scale=2), nullable=False, default=0)
    vat_rate = Column(Numeric(precision=5, scale=2), nullable=False, default=20.0)

    # Calculated fields (stored for efficiency)
    discount_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    net_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    vat_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    gross_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)

    @hybrid_property
    def subtotal(self):
        """Calculate subtotal (quantity * unit_price)"""
        return self.quantity * self.unit_price

    def calculate_amounts(self):
        """Calculate all monetary amounts for this item"""
        # Calculate subtotal
        subtotal = Decimal(self.quantity) * Decimal(self.unit_price)

        # Calculate discount
        self.discount_amount = Decimal(subtotal) * (Decimal(self.discount_percentage) / 100)

        # Calculate net amount (after discount)
        self.net_amount = subtotal - self.discount_amount

        # Calculate VAT
        self.vat_amount = self.net_amount * (Decimal(self.vat_rate) / 100)

        # Calculate gross amount (including VAT)
        self.gross_amount = self.net_amount + self.vat_amount

    def __repr__(self):
        return f"<InvoiceItem {self.product_id} - {self.quantity}>"
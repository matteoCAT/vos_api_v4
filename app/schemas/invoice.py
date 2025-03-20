from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.models.invoice import PaymentStatus
from app.schemas.supplier import Supplier


class InvoiceItemBase(BaseModel):
    """Base schema for Invoice Item data"""
    product_id: UUID = Field(..., description="Product ID")
    description: Optional[str] = Field(None, description="Item description")
    quantity: Decimal = Field(..., description="Quantity")
    unit_id: UUID = Field(..., description="Unit ID")
    unit_price: Decimal = Field(..., description="Unit price")
    discount_percentage: Decimal = Field(0, description="Discount percentage")
    vat_rate: Decimal = Field(20.0, description="VAT rate")


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating a new invoice item"""

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "00000000-0000-0000-0000-000000000000",
                "description": "Mineral Water (500ml)",
                "quantity": 10,
                "unit_id": "00000000-0000-0000-0000-000000000000",
                "unit_price": 12.99,
                "discount_percentage": 5.0,
                "vat_rate": 20.0
            }
        }


class InvoiceItemUpdate(BaseModel):
    """Schema for updating an invoice item"""
    product_id: Optional[UUID] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_id: Optional[UUID] = None
    unit_price: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 15,
                "discount_percentage": 10.0
            }
        }


class InvoiceItemInDBBase(InvoiceItemBase):
    """Schema for Invoice Item data as stored in DB"""
    id: UUID
    invoice_id: UUID
    discount_amount: Decimal
    net_amount: Decimal
    vat_amount: Decimal
    gross_amount: Decimal

    class Config:
        from_attributes = True


class InvoiceItem(InvoiceItemInDBBase):
    """Schema for Invoice Item data returned to client"""
    pass


class InvoiceItemDetail(InvoiceItem):
    """Schema for Invoice Item with product and unit details"""
    product_name: Optional[str] = None
    unit_name: Optional[str] = None
    unit_symbol: Optional[str] = None


class InvoiceBase(BaseModel):
    """Base schema for Invoice data"""
    invoice_number: str = Field(..., description="Invoice number from supplier")
    reference: Optional[str] = Field(None, description="Internal reference")
    supplier_id: UUID = Field(..., description="Supplier ID")

    # Order and delivery fields
    order_date: Optional[date] = Field(None, description="Date when the order was placed")
    order_number: Optional[str] = Field(None, description="Order/PO number")
    delivery_date: Optional[date] = Field(None, description="Date when goods were delivered")
    delivery_note: Optional[str] = Field(None, description="Delivery note reference")

    # Invoice dates
    invoice_date: date = Field(..., description="Invoice date")
    due_date: date = Field(..., description="Due date")
    received_date: Optional[date] = Field(None, description="Date invoice was received")

    # Payment information
    payment_status: PaymentStatus = Field(PaymentStatus.PENDING, description="Payment status")
    payment_date: Optional[date] = Field(None, description="Date payment was made")
    payment_reference: Optional[str] = Field(None, description="Payment reference")
    payment_method: Optional[str] = Field(None, description="Method of payment")

    # Notes
    notes: Optional[str] = Field(None, description="Notes")

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'invoice_date' in values and values['invoice_date'] and v < values['invoice_date']:
            raise ValueError("Due date cannot be before invoice date")
        return v


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice"""
    items: List[InvoiceItemCreate] = Field([], description="Invoice items")

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-12345",
                "reference": "REF-001",
                "supplier_id": "00000000-0000-0000-0000-000000000000",
                "order_date": "2023-01-01",
                "order_number": "PO-12345",
                "delivery_date": "2023-01-10",
                "delivery_note": "DN-98765",
                "invoice_date": "2023-01-15",
                "due_date": "2023-02-14",
                "received_date": "2023-01-16",
                "payment_method": "Bank Transfer",
                "notes": "January food order",
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000000",
                        "quantity": 10,
                        "unit_id": "00000000-0000-0000-0000-000000000000",
                        "unit_price": 12.99,
                        "discount_percentage": 5.0
                    }
                ]
            }
        }


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice"""
    invoice_number: Optional[str] = None
    reference: Optional[str] = None
    supplier_id: Optional[UUID] = None

    # Order and delivery fields
    order_date: Optional[date] = None
    order_number: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_note: Optional[str] = None

    # Invoice dates
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    received_date: Optional[date] = None

    # Payment information
    payment_status: Optional[PaymentStatus] = None
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    payment_method: Optional[str] = None

    # Notes
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "payment_status": "paid",
                "payment_date": "2023-01-15",
                "payment_reference": "BANK-12345",
                "payment_method": "Bank Transfer",
                "delivery_date": "2023-01-12",
                "delivery_note": "DN-98765-UPDATED"
            }
        }


class InvoiceInDBBase(InvoiceBase):
    """Schema for Invoice data as stored in DB"""
    id: UUID
    subtotal: Decimal
    total_discount: Decimal
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal

    class Config:
        from_attributes = True


class Invoice(InvoiceInDBBase):
    """Schema for Invoice data returned to client"""
    pass


class InvoiceDetail(Invoice):
    """Schema for Invoice with supplier details and items"""
    supplier: Optional[Supplier] = None
    items: List[InvoiceItemDetail] = []
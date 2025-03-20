"""
Script to seed sample invoices in the database.
"""
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.invoice import Invoice, InvoiceItem, PaymentStatus
from app.models.product import Product
from app.models.supplier import Supplier


def init_invoices(db: Session) -> None:
    """
    Initialize sample invoices in database
    """
    # Get a supplier (or create one if none exists)
    supplier = db.query(Supplier).first()
    if not supplier:
        supplier = Supplier(
            name="ABC Foods Inc",
            contact_name="John Smith",
            email="john@abcfoods.com",
            phone="+1234567890",
            address="123 Main St, Anytown, USA",
            tax_id="12-3456789",
            website="https://www.abcfoods.example.com",
            is_active=True,
            notes="Main food supplier"
        )
        db.add(supplier)
        db.flush()
        print("Created sample supplier: ABC Foods Inc")

    # Get products
    products = db.query(Product).all()

    if not products:
        print("Warning: No products found. Run seed_products.py first.")
        return

    # Create sample invoices
    today = date.today()

    invoices = [
        # Paid invoice from last month
        {
            "invoice_number": "INV-12345",
            "reference": "PO-001",
            "supplier_id": supplier.id,
            "order_date": today - timedelta(days=40),
            "order_number": "PO-12345",
            "delivery_date": today - timedelta(days=32),
            "delivery_note": "DN-98765",
            "invoice_date": today - timedelta(days=30),
            "due_date": today - timedelta(days=15),
            "received_date": today - timedelta(days=28),
            "payment_status": PaymentStatus.PAID,
            "payment_date": today - timedelta(days=20),
            "payment_reference": "BANK-12345",
            "payment_method": "Bank Transfer",
            "notes": "Monthly food order",
            "items": [
                {
                    "product_id": products[0].id,
                    "description": products[0].name,
                    "quantity": 5,
                    "unit_id": products[0].purchase_unit_id,
                    "unit_price": float(products[0].base_price),
                    "discount_percentage": 5.0,
                    "vat_rate": float(products[0].vat_rate)
                },
                {
                    "product_id": products[1].id if len(products) > 1 else products[0].id,
                    "description": products[1].name if len(products) > 1 else products[0].name,
                    "quantity": 10,
                    "unit_id": products[1].purchase_unit_id if len(products) > 1 else products[0].purchase_unit_id,
                    "unit_price": float(products[1].base_price) if len(products) > 1 else float(products[0].base_price),
                    "discount_percentage": 0,
                    "vat_rate": float(products[1].vat_rate) if len(products) > 1 else float(products[0].vat_rate)
                }
            ]
        },
        # Pending invoice from this week
        {
            "invoice_number": "INV-67890",
            "reference": "PO-002",
            "supplier_id": supplier.id,
            "order_date": today - timedelta(days=10),
            "order_number": "PO-67890",
            "delivery_date": today - timedelta(days=3),
            "delivery_note": "DN-12345",
            "invoice_date": today - timedelta(days=2),
            "due_date": today + timedelta(days=28),
            "received_date": today - timedelta(days=1),
            "payment_status": PaymentStatus.PENDING,
            "notes": "Weekly food order",
            "items": [
                {
                    "product_id": products[0].id,
                    "description": products[0].name,
                    "quantity": 3,
                    "unit_id": products[0].purchase_unit_id,
                    "unit_price": float(products[0].base_price),
                    "discount_percentage": 0,
                    "vat_rate": float(products[0].vat_rate)
                }
            ]
        },
        # Overdue invoice
        {
            "invoice_number": "INV-54321",
            "reference": "PO-003",
            "supplier_id": supplier.id,
            "order_date": today - timedelta(days=60),
            "order_number": "PO-54321",
            "delivery_date": today - timedelta(days=52),
            "delivery_note": "DN-54321",
            "invoice_date": today - timedelta(days=50),
            "due_date": today - timedelta(days=20),
            "received_date": today - timedelta(days=48),
            "payment_status": PaymentStatus.OVERDUE,
            "notes": "Special order",
            "items": [
                {
                    "product_id": products[-1].id,
                    "description": products[-1].name,
                    "quantity": 2,
                    "unit_id": products[-1].purchase_unit_id,
                    "unit_price": float(products[-1].base_price) * 1.2,  # Special price
                    "discount_percentage": 0,
                    "vat_rate": float(products[-1].vat_rate)
                }
            ]
        }
    ]

    # Add invoices to database
    for invoice_data in invoices:
        # Extract items
        items_data = invoice_data.pop("items")

        # Check if invoice already exists
        existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_data["invoice_number"]).first()
        if existing_invoice:
            print(f"Invoice {invoice_data['invoice_number']} already exists, skipping")
            continue

        # Create invoice
        invoice = Invoice(**invoice_data)
        db.add(invoice)
        db.flush()  # To get the ID

        # Add items
        for item_data in items_data:
            item = InvoiceItem(invoice_id=invoice.id, **item_data)
            item.calculate_amounts()
            db.add(item)

        db.flush()

        # Update invoice totals
        invoice.update_totals()

        print(f"Added invoice {invoice.invoice_number} with {len(items_data)} items")

    db.commit()


def main() -> None:
    """
    Main function to run the script
    """
    db = SessionLocal()
    try:
        init_invoices(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
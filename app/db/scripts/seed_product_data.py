"""
Combined script to seed all initial data in the database.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_product_units import init_product_units
from seed_product_formats import init_product_formats
from seed_products import init_products
from seed_invoices import init_invoices
from app.db.session import SessionLocal


def main() -> None:
    """
    Initialize all data
    """
    print("Seeding database with initial data...")
    db = SessionLocal()
    try:
        print("\n--- Seeding Product Units ---")
        init_product_units(db)

        print("\n--- Seeding Product Formats ---")
        init_product_formats(db)

        print("\n--- Seeding Sample Products ---")
        init_products(db)

        print("\n--- Seeding Sample Invoices ---")
        init_invoices(db)

        print("\nData seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
"""
Script to seed sample products in the database.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.product import Product, ProductType
from app.models.product_unit import ProductUnit
from app.models.product_format import ProductFormat


def init_products(db: Session) -> None:
    """
    Initialize sample products in database
    """
    # Get existing units
    kg_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "kg").first()
    g_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "g").first()
    unit_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "unit").first()
    bottle_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "btl").first()
    case_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "case").first()
    can_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "can").first()

    # Get existing formats
    bottle_500ml = db.query(ProductFormat).filter(ProductFormat.name == "500ml Bottle").first()
    can_330ml = db.query(ProductFormat).filter(ProductFormat.name == "330ml Can").first()

    # Skip if units or formats don't exist
    if not all([kg_unit, g_unit, unit_unit, bottle_unit, case_unit, can_unit, bottle_500ml, can_330ml]):
        print(
            "Warning: Some units or formats are missing. Run seed_product_units.py and seed_product_formats.py first.")
        return

    # Define sample products
    products = [
        # Unit-based products
        {
            "name": "Mineral Water (500ml)",
            "code": "BEV001",
            "description": "Natural mineral water in 500ml bottles",
            "product_type": ProductType.UNIT,
            "base_price": 12.99,  # Price per case
            "is_active": True,
            "purchasable": True,
            "sellable": True,
            "purchase_unit_id": case_unit.id,
            "sales_unit_id": bottle_unit.id,
            "default_format_id": bottle_500ml.id,
            "conversion_factor": 24.0  # 24 bottles per case
        },
        {
            "name": "Soda Can (330ml)",
            "code": "BEV002",
            "description": "Carbonated soft drink in 330ml cans",
            "product_type": ProductType.UNIT,
            "base_price": 18.50,  # Price per case
            "is_active": True,
            "purchasable": True,
            "sellable": True,
            "purchase_unit_id": case_unit.id,
            "sales_unit_id": can_unit.id,
            "default_format_id": can_330ml.id,
            "conversion_factor": 24.0  # 24 cans per case
        },

        # Weight-based products
        {
            "name": "Premium Ham",
            "code": "MEAT001",
            "description": "High-quality sliced ham",
            "product_type": ProductType.WEIGHT,
            "base_price": 8.99,  # Price per kg
            "price_per_kg": 8.99,
            "is_active": True,
            "purchasable": True,
            "sellable": True,
            "purchase_unit_id": kg_unit.id,
            "sales_unit_id": g_unit.id,
            "default_format_id": None,
            "conversion_factor": 1000.0  # 1000g = 1kg
        },
        {
            "name": "Aged Cheese",
            "code": "DAIRY001",
            "description": "Premium aged cheese",
            "product_type": ProductType.WEIGHT,
            "base_price": 12.50,  # Price per kg
            "price_per_kg": 12.50,
            "is_active": True,
            "purchasable": True,
            "sellable": True,
            "purchase_unit_id": kg_unit.id,
            "sales_unit_id": g_unit.id,
            "default_format_id": None,
            "conversion_factor": 1000.0  # 1000g = 1kg
        },

        # Case products
        {
            "name": "Canned Tomatoes",
            "code": "GROC001",
            "description": "Italian peeled tomatoes",
            "product_type": ProductType.CASE,
            "base_price": 24.00,  # Price per case
            "is_active": True,
            "purchasable": True,
            "sellable": True,
            "purchase_unit_id": case_unit.id,
            "sales_unit_id": can_unit.id,
            "default_format_id": None,
            "conversion_factor": 12.0  # 12 cans per case
        }
    ]

    # Add products to database if they don't exist
    for product_data in products:
        product = db.query(Product).filter(Product.code == product_data["code"]).first()
        if not product:
            product = Product(**product_data)
            db.add(product)

    db.commit()
    print(f"Added {len(products)} sample products")


def main() -> None:
    """
    Main function to run the script
    """
    db = SessionLocal()
    try:
        init_products(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
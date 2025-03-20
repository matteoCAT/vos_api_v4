"""
Script to seed initial product formats in the database.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.product_format import ProductFormat
from app.models.product_unit import ProductUnit


def init_product_formats(db: Session) -> None:
    """
    Initialize product formats in database
    """
    # Get existing units
    liter_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "L").first()
    ml_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "ml").first()
    kg_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "kg").first()
    g_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "g").first()
    bottle_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "btl").first()
    can_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "can").first()
    package_unit = db.query(ProductUnit).filter(ProductUnit.symbol == "pkg").first()

    # Skip if units don't exist
    if not all([liter_unit, ml_unit, kg_unit, g_unit, bottle_unit, can_unit, package_unit]):
        print("Warning: Some units are missing. Run seed_product_units.py first.")
        return

    # Define formats
    formats = []

    # Bottle formats (by volume)
    if bottle_unit and liter_unit:
        formats.extend([
            {
                "name": "330ml Bottle",
                "description": "Small 330ml bottle",
                "value": 330,
                "unit_id": ml_unit.id,
                "is_standard": True
            },
            {
                "name": "500ml Bottle",
                "description": "Medium 500ml bottle",
                "value": 500,
                "unit_id": ml_unit.id,
                "is_standard": True
            },
            {
                "name": "750ml Bottle",
                "description": "Wine size 750ml bottle",
                "value": 750,
                "unit_id": ml_unit.id,
                "is_standard": True
            },
            {
                "name": "1L Bottle",
                "description": "Standard 1 liter bottle",
                "value": 1,
                "unit_id": liter_unit.id,
                "is_standard": True
            },
            {
                "name": "1.5L Bottle",
                "description": "Large 1.5 liter bottle",
                "value": 1.5,
                "unit_id": liter_unit.id,
                "is_standard": True
            },
            {
                "name": "2L Bottle",
                "description": "Extra large 2 liter bottle",
                "value": 2,
                "unit_id": liter_unit.id,
                "is_standard": True
            },
        ])

    # Can formats
    if can_unit and g_unit and ml_unit:
        formats.extend([
            {
                "name": "330ml Can",
                "description": "Standard beverage can",
                "value": 330,
                "unit_id": ml_unit.id,
                "is_standard": True
            },
            {
                "name": "250g Can",
                "description": "Small food can",
                "value": 250,
                "unit_id": g_unit.id,
                "is_standard": True
            },
            {
                "name": "400g Can",
                "description": "Medium food can",
                "value": 400,
                "unit_id": g_unit.id,
                "is_standard": True
            },
        ])

    # Package formats
    if package_unit and g_unit and kg_unit:
        formats.extend([
            {
                "name": "100g Package",
                "description": "Small package",
                "value": 100,
                "unit_id": g_unit.id,
                "is_standard": True
            },
            {
                "name": "250g Package",
                "description": "Standard package",
                "value": 250,
                "unit_id": g_unit.id,
                "is_standard": True
            },
            {
                "name": "500g Package",
                "description": "Medium package",
                "value": 500,
                "unit_id": g_unit.id,
                "is_standard": True
            },
            {
                "name": "1kg Package",
                "description": "Large package",
                "value": 1,
                "unit_id": kg_unit.id,
                "is_standard": True
            },
        ])

    # Add formats to database if they don't exist
    for format_data in formats:
        format_obj = db.query(ProductFormat).filter(ProductFormat.name == format_data["name"]).first()
        if not format_obj:
            format_obj = ProductFormat(**format_data)
            db.add(format_obj)

    db.commit()
    print(f"Added {len(formats)} product formats")


def main() -> None:
    """
    Main function to run the script
    """
    db = SessionLocal()
    try:
        init_product_formats(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
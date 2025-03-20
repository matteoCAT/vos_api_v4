"""
Script to seed initial product units in the database.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.product_unit import ProductUnit
from app.core.config import settings


def init_product_units(db: Session) -> None:
    """
    Initialize product units in database
    """
    # Weight units
    weight_units = [
        {
            "name": "Kilogram",
            "symbol": "kg",
            "description": "Standard weight measurement",
            "is_base_unit": True,
            "purchasable": True,
            "sellable": True
        },
        {
            "name": "Gram",
            "symbol": "g",
            "description": "1/1000 of a kilogram",
            "is_base_unit": False,
            "purchasable": False,
            "sellable": True
        },
    ]

    # Volume units
    volume_units = [
        {
            "name": "Liter",
            "symbol": "L",
            "description": "Standard volume measurement",
            "is_base_unit": True,
            "purchasable": True,
            "sellable": True
        },
        {
            "name": "Milliliter",
            "symbol": "ml",
            "description": "1/1000 of a liter",
            "is_base_unit": False,
            "purchasable": False,
            "sellable": True
        },
    ]

    # Quantity units
    quantity_units = [
        {
            "name": "Unit",
            "symbol": "unit",
            "description": "Single unit",
            "is_base_unit": True,
            "purchasable": True,
            "sellable": True
        },
        {
            "name": "Dozen",
            "symbol": "dz",
            "description": "12 units",
            "is_base_unit": False,
            "purchasable": True,
            "sellable": False
        },
        {
            "name": "Box",
            "symbol": "box",
            "description": "Container box - quantity depends on the product",
            "is_base_unit": False,
            "purchasable": True,
            "sellable": False
        },
        {
            "name": "Case",
            "symbol": "case",
            "description": "Case containing multiple units - quantity depends on the product",
            "is_base_unit": False,
            "purchasable": True,
            "sellable": False
        },
        {
            "name": "Package",
            "symbol": "pkg",
            "description": "Packaged product - quantity depends on the product",
            "is_base_unit": False,
            "purchasable": True,
            "sellable": True
        },
        {
            "name": "Bottle",
            "symbol": "btl",
            "description": "Bottle - volume depends on the product",
            "is_base_unit": False,
            "purchasable": True,
            "sellable": True
        },
        {
            "name": "Can",
            "symbol": "can",
            "description": "Can - volume/weight depends on the product",
            "is_base_unit": False,
            "purchasable": True,
            "sellable": True
        },
    ]

    # Restaurant-specific units
    restaurant_units = [
        {
            "name": "Portion",
            "symbol": "ptn",
            "description": "Single serving portion",
            "is_base_unit": False,
            "purchasable": False,
            "sellable": True
        },
        {
            "name": "Plate",
            "symbol": "plt",
            "description": "Single plate serving",
            "is_base_unit": False,
            "purchasable": False,
            "sellable": True
        },
    ]

    # Combine all units
    all_units = weight_units + volume_units + quantity_units + restaurant_units

    # Add units to database if they don't exist
    for unit_data in all_units:
        unit = db.query(ProductUnit).filter(ProductUnit.name == unit_data["name"]).first()
        if not unit:
            unit = ProductUnit(**unit_data)
            db.add(unit)

    db.commit()
    print(f"Added {len(all_units)} product units")


def main() -> None:
    """
    Main function to run the script
    """
    db = SessionLocal()
    try:
        init_product_units(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.product_unit import ProductUnit
from app.schemas.product_unit import ProductUnitCreate, ProductUnitUpdate


class CRUDProductUnit(CRUDBase[ProductUnit, ProductUnitCreate, ProductUnitUpdate]):
    """
    CRUD operations for ProductUnit model
    """

    def get_by_name(self, db: Session, *, name: str) -> Optional[ProductUnit]:
        """
        Get a product unit by name

        Args:
            db: Database session
            name: Product unit name

        Returns:
            Optional[ProductUnit]: ProductUnit instance if found, None otherwise
        """
        return db.query(ProductUnit).filter(ProductUnit.name == name).first()

    def get_by_symbol(self, db: Session, *, symbol: str) -> Optional[ProductUnit]:
        """
        Get a product unit by symbol

        Args:
            db: Database session
            symbol: Product unit symbol

        Returns:
            Optional[ProductUnit]: ProductUnit instance if found, None otherwise
        """
        return db.query(ProductUnit).filter(ProductUnit.symbol == symbol).first()

    def get_all_purchasable(self, db: Session, *, skip: int = 0, limit: int = 100):
        """
        Get all purchasable product units

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductUnit]: List of purchasable product units
        """
        return db.query(ProductUnit).filter(ProductUnit.purchasable == True).offset(skip).limit(limit).all()

    def get_all_sellable(self, db: Session, *, skip: int = 0, limit: int = 100):
        """
        Get all sellable product units

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductUnit]: List of sellable product units
        """
        return db.query(ProductUnit).filter(ProductUnit.sellable == True).offset(skip).limit(limit).all()

    def get_base_units(self, db: Session, *, skip: int = 0, limit: int = 100):
        """
        Get all base product units

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductUnit]: List of base product units
        """
        return db.query(ProductUnit).filter(ProductUnit.is_base_unit == True).offset(skip).limit(limit).all()


product_unit_crud = CRUDProductUnit(ProductUnit)
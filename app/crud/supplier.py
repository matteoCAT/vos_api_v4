from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    """
    CRUD operations for Supplier model
    """

    def get_by_name(self, db: Session, *, name: str) -> Optional[Supplier]:
        """
        Get a supplier by name

        Args:
            db: Database session
            name: Supplier name

        Returns:
            Optional[Supplier]: Supplier instance if found, None otherwise
        """
        return db.query(Supplier).filter(Supplier.name == name).first()

    def get_by_tax_id(self, db: Session, *, tax_id: str) -> Optional[Supplier]:
        """
        Get a supplier by tax ID

        Args:
            db: Database session
            tax_id: Supplier tax ID

        Returns:
            Optional[Supplier]: Supplier instance if found, None otherwise
        """
        return db.query(Supplier).filter(Supplier.tax_id == tax_id).first()

    def get_active(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Supplier]:
        """
        Get active suppliers with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of active supplier instances
        """
        return db.query(Supplier).filter(Supplier.is_active == True).offset(skip).limit(limit).all()


# Create an instance of the CRUD class
supplier = CRUDSupplier(Supplier)
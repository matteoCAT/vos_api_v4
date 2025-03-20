from typing import Optional, List, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.product_format import ProductFormat
from app.schemas.product_format import ProductFormatCreate, ProductFormatUpdate


class CRUDProductFormat(CRUDBase[ProductFormat, ProductFormatCreate, ProductFormatUpdate]):
    """
    CRUD operations for ProductFormat model
    """

    def get_by_name(self, db: Session, *, name: str) -> Optional[ProductFormat]:
        """
        Get a product format by name

        Args:
            db: Database session
            name: Product format name

        Returns:
            Optional[ProductFormat]: ProductFormat instance if found, None otherwise
        """
        return db.query(ProductFormat).filter(ProductFormat.name == name).first()

    def get_by_unit(self, db: Session, *, unit_id: UUID, skip: int = 0, limit: int = 100) -> List[ProductFormat]:
        """
        Get all product formats for a specific unit

        Args:
            db: Database session
            unit_id: Unit ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductFormat]: List of product formats for the unit
        """
        return db.query(ProductFormat).filter(ProductFormat.unit_id == unit_id).offset(skip).limit(limit).all()

    def get_standard_formats(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ProductFormat]:
        """
        Get all standard product formats

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductFormat]: List of standard product formats
        """
        return db.query(ProductFormat).filter(ProductFormat.is_standard == True).offset(skip).limit(limit).all()


product_format_crud = CRUDProductFormat(ProductFormat)
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.product import Product, ProductType
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """
    CRUD operations for Product model
    """

    def get_by_code(self, db: Session, *, code: str) -> Optional[Product]:
        """
        Get a product by code

        Args:
            db: Database session
            code: Product code

        Returns:
            Optional[Product]: Product instance if found, None otherwise
        """
        return db.query(Product).filter(Product.code == code).first()

    def search(
            self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Search products by name or code

        Args:
            db: Database session
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Product]: List of matching products
        """
        search_query = f"%{query}%"
        return (
            db.query(Product)
            .filter(
                or_(
                    Product.name.ilike(search_query),
                    Product.code.ilike(search_query),
                    Product.description.ilike(search_query)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get all active products

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Product]: List of active products
        """
        return (
            db.query(Product)
            .filter(Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
            self, db: Session, *, product_type: ProductType, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get products by type

        Args:
            db: Database session
            product_type: Product type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Product]: List of products of the specified type
        """
        return (
            db.query(Product)
            .filter(Product.product_type == product_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_purchasable(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get all purchasable products

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Product]: List of purchasable products
        """
        return (
            db.query(Product)
            .filter(Product.purchasable == True, Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_sellable(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get all sellable products

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Product]: List of sellable products
        """
        return (
            db.query(Product)
            .filter(Product.sellable == True, Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )


product_crud = CRUDProduct(Product)
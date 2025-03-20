from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate


class CRUDSite(CRUDBase[Site, SiteCreate, SiteUpdate]):
    """
    CRUD operations for Site model
    """

    def get_by_name(self, db: Session, *, name: str) -> Optional[Site]:
        """
        Get a site by name

        Args:
            db: Database session
            name: Site name

        Returns:
            Optional[Site]: Site instance if found, None otherwise
        """
        return db.query(Site).filter(Site.name == name).first()

    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Site]:
        """
        Get all active sites

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Site]: List of active site instances
        """
        return (
            db.query(Site)
            .filter(Site.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_manager(self, db: Session, *, manager_id: Any, skip: int = 0, limit: int = 100) -> List[Site]:
        """
        Get all sites managed by a specific user

        Args:
            db: Database session
            manager_id: Manager user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Site]: List of site instances
        """
        return (
            db.query(Site)
            .filter(Site.manager_id == manager_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
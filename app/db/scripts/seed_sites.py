#!/usr/bin/env python3
"""
Script to seed sample site data into the database
"""
import logging
import sys
import os
from typing import Optional

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
import uuid

from app.db.session import SessionLocal
from app.models.site import Site
from app.models.user import User, UserRole
from app.crud.user import CRUDUser
from app.crud.site import CRUDSite
from app.schemas.user import UserCreate
from app.schemas.site import SiteCreate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

site_crud = CRUDSite(Site)
user_crud = CRUDUser(User)


def get_or_create_manager(db: Session) -> User:
    """
    Get an existing manager user or create a new one
    """
    # Try to find existing manager
    manager = db.query(User).filter(User.role == UserRole.MANAGER).first()

    if manager:
        logger.info(f"Using existing manager: {manager.email}")
        return manager

    # Create a new manager if none exists
    logger.info("Creating a new manager user")
    manager_data = UserCreate(
        email="manager@restaurant.com",
        username="manager",
        password="restaurantmanager123",
        name="Site",
        surname="Manager",
        telephone="+1234567890",
        role=UserRole.MANAGER,
        is_active=True
    )

    return user_crud.create(db, obj_in=manager_data)


def seed_sites(db: Session) -> None:
    """
    Seed sample sites into the database
    """
    # Get or create a manager user
    manager = get_or_create_manager(db)

    # Sample site data
    sites = [
        {
            "name": "Downtown Restaurant",
            "address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA",
            "phone": "+1234567890",
            "email": "downtown@restaurant.com",
            "manager_id": manager.id
        },
        {
            "name": "Seaside Restaurant",
            "address": "456 Ocean Avenue",
            "city": "Miami",
            "state": "FL",
            "zip_code": "33139",
            "country": "USA",
            "phone": "+1987654321",
            "email": "seaside@restaurant.com",
            "manager_id": manager.id
        }
    ]

    # Create sites
    for site_data in sites:
        # Check if site with this name already exists
        existing_site = site_crud.get_by_name(db, name=site_data["name"])
        if existing_site:
            logger.info(f"Site already exists: {site_data['name']}")
            continue

        # Create site
        site = site_crud.create(db, obj_in=SiteCreate(**site_data))
        logger.info(f"Created site: {site.name}")


def main() -> None:
    """
    Main function to seed the database
    """
    logger.info("Creating sample sites")
    db = SessionLocal()
    try:
        seed_sites(db)
        logger.info("Sites seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding sites: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.site import Site
from app.schemas.site import Site as SiteSchema, SiteCreate, SiteUpdate, SiteWithDetails
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.site import CRUDSite

router = APIRouter()
site_crud = CRUDSite(Site)


@router.get("/", response_model=List[SiteSchema], summary="Get all sites")
def get_sites(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        current_user: User = Depends(check_user_permissions(["view_sites"]))
):
    """
    Retrieve all sites.

    - **skip**: Number of sites to skip
    - **limit**: Maximum number of sites to return
    - **active_only**: Filter to only active sites
    """
    if active_only:
        sites = site_crud.get_active(db, skip=skip, limit=limit)
    else:
        sites = site_crud.get_multi(db, skip=skip, limit=limit)
    return sites


@router.post("/", response_model=SiteSchema, summary="Create new site")
def create_site(
        *,
        db: Session = Depends(get_db),
        site_in: SiteCreate,
        current_user: User = Depends(check_user_permissions(["create_sites"]))
):
    """
    Create a new site.
    """
    # Check if site with this name already exists
    site = site_crud.get_by_name(db, name=site_in.name)
    if site:
        raise HTTPException(
            status_code=400,
            detail="A site with this name already exists."
        )

    # Create new site
    site = site_crud.create(db, obj_in=site_in)
    return site


@router.get("/manager/{manager_id}", response_model=List[SiteSchema], summary="Get sites by manager")
def get_sites_by_manager(
        *,
        db: Session = Depends(get_db),
        manager_id: UUID = Path(..., description="The ID of the manager"),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(check_user_permissions(["view_sites"]))
):
    """
    Retrieve all sites managed by a specific user.

    - **manager_id**: ID of the manager user
    - **skip**: Number of sites to skip
    - **limit**: Maximum number of sites to return
    """
    sites = site_crud.get_by_manager(db, manager_id=manager_id, skip=skip, limit=limit)
    return sites


@router.get("/{site_id}", response_model=SiteSchema, summary="Get site by ID")
def get_site(
        *,
        db: Session = Depends(get_db),
        site_id: UUID = Path(..., description="The ID of the site to get"),
        current_user: User = Depends(check_user_permissions(["view_sites"]))
):
    """
    Get a specific site by ID.
    """
    site = site_crud.get(db, id=site_id)
    if not site:
        raise HTTPException(
            status_code=404,
            detail="Site not found"
        )
    return site


@router.put("/{site_id}", response_model=SiteSchema, summary="Update site")
def update_site(
        *,
        db: Session = Depends(get_db),
        site_id: UUID = Path(..., description="The ID of the site to update"),
        site_in: SiteUpdate,
        current_user: User = Depends(check_user_permissions(["update_sites"]))
):
    """
    Update a site.
    """
    site = site_crud.get(db, id=site_id)
    if not site:
        raise HTTPException(
            status_code=404,
            detail="Site not found"
        )

    # Prevent name duplicates if updating name
    if site_in.name and site_in.name != site.name:
        existing_site = site_crud.get_by_name(db, name=site_in.name)
        if existing_site:
            raise HTTPException(
                status_code=400,
                detail="A site with this name already exists."
            )

    site = site_crud.update(db, db_obj=site, obj_in=site_in)
    return site


@router.delete("/{site_id}", response_model=SiteSchema, summary="Delete site")
def delete_site(
        *,
        db: Session = Depends(get_db),
        site_id: UUID = Path(..., description="The ID of the site to delete"),
        current_user: User = Depends(check_user_permissions(["delete_sites"]))
):
    """
    Delete a site.
    """
    site = site_crud.get(db, id=site_id)
    if not site:
        raise HTTPException(
            status_code=404,
            detail="Site not found"
        )

    site = site_crud.remove(db, id=site_id)
    return site
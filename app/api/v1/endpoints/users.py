from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.core.security import get_current_active_user, check_user_permissions
from app.db.session import get_db
from app.crud.user import CRUDUser

router = APIRouter()
user_crud = CRUDUser(User)


@router.get("/", response_model=List[UserSchema], summary="Get all users")
def get_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(check_user_permissions(["view_users"]))
):
    """
    Retrieve all users.

    - **skip**: Number of users to skip
    - **limit**: Maximum number of users to return
    """
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserSchema, summary="Create new user")
def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
        current_user: User = Depends(check_user_permissions(["create_users"]))
):
    """
    Create a new user.
    """
    # Check if user with this email already exists
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )

    # Create new user
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserSchema, summary="Get current user")
def get_user_me(
        current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    """
    return current_user


@router.get("/{user_id}", response_model=UserSchema, summary="Get user by ID")
def get_user(
        *,
        db: Session = Depends(get_db),
        user_id: UUID = Path(..., description="The ID of the user to get"),
        current_user: User = Depends(check_user_permissions(["view_users"]))
):
    """
    Get a specific user by ID.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema, summary="Update user")
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: UUID = Path(..., description="The ID of the user to update"),
        user_in: UserUpdate,
        current_user: User = Depends(check_user_permissions(["update_users"]))
):
    """
    Update a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent email duplicates if updating email
    if user_in.email and user_in.email != user.email:
        existing_user = user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists."
            )

    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=UserSchema, summary="Delete user")
def delete_user(
        *,
        db: Session = Depends(get_db),
        user_id: UUID = Path(..., description="The ID of the user to delete"),
        current_user: User = Depends(check_user_permissions(["delete_users"]))
):
    """
    Delete a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves"
        )

    user = user_crud.remove(db, id=user_id)
    return user
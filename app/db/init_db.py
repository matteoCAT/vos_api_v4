import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
import uuid
from app.db.session import get_db, engine
from app.core.security import get_password_hash
from app.models.user import User, Role

# Create tables if they don't exist
from app.db.session import Base

Base.metadata.create_all(bind=engine)


def seed_database():
    db = next(get_db())

    # Create roles if they don't exist
    roles = {
        "admin": "Full system access with all permissions",
        "owner": "Business owner with high-level access",
        "manager": "Restaurant manager with operational access",
        "supervisor": "Shift supervisor with limited management capabilities",
        "staff": "Regular staff with basic access"
    }

    # Dictionary to store created roles
    created_roles = {}

    for role_name, description in roles.items():
        # Check if role exists
        existing_role = db.query(Role).filter(Role.name == role_name).first()

        if not existing_role:
            # Define permissions based on role
            permissions = ""
            if role_name == "admin":
                permissions = "all"
            elif role_name == "owner":
                permissions = "manage_users,manage_products,manage_recipes,manage_invoices,view_reports"
            elif role_name == "manager":
                permissions = "manage_products,manage_recipes,manage_invoices,view_reports"
            elif role_name == "supervisor":
                permissions = "manage_products,manage_recipes,view_invoices"
            elif role_name == "staff":
                permissions = "view_products,view_recipes,create_invoices"

            # Create role
            new_role = Role(
                name=role_name,
                description=description,
                permissions=permissions
            )

            db.add(new_role)
            db.commit()
            db.refresh(new_role)

            created_roles[role_name] = new_role
            print(f"Created role: {role_name}")
        else:
            created_roles[role_name] = existing_role
            print(f"Role already exists: {role_name}")

    # Check if any user exists
    user_exists = db.query(User).first() is not None

    if not user_exists and "admin" in created_roles:
        admin_role = created_roles["admin"]

        admin_user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            username="admin",
            name="Admin",
            surname="User",
            telephone="+1234567890",
            hashed_password=get_password_hash("teo270383"),
            role=admin_role.name,
            role_id=admin_role.id,  # Use the role ID from the created role
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        print("Admin user created successfully!")
    else:
        print("Users already exist in the database.")


if __name__ == "__main__":
    seed_database()
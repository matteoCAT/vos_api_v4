# app/db/base.py
from app.db.session import Base  # Import the Base class from session
from app.models.user import User  # Import your models
from app.models.supplier import Supplier
# Import other models as you create them
# from app.models.product import Product
# from app.models.recipe import Recipe
# from app.models.invoice import Invoice

# This file exists to import all models so that Base has them registered
# when create_all() is called
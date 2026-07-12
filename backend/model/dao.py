import uuid
import bcrypt

from datetime import datetime
from typing import Union, Literal
from fastapi import HTTPException


from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError


from .database import get_db, SessionLocal


from .model import BaseModel, User, Role, Vehicle, Driver, Trip, MaintenanceLog


class UserDAO:
    @classmethod
    def create_user(cls, db, username: str, password: str, role_id: int):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # assign role_id to the `role_id` column
        new_user = User(username=username, password=hashed_password.decode('utf-8'), role=role_id)
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Username already exists")

    @classmethod
    def get_user_by_username(cls, db, username: str):
        """Return a User by username or None."""
        return db.query(User).filter(User.username == username).first()


def seed_admin(admin_username: str = "admin", admin_password: str = "admin@123"):
    """Create a default 'admin' role and user if they don't exist.

    This function uses a local SessionLocal() so it can be called safely at runtime,
    not at import time.
    """
    with SessionLocal() as session:
        # create admin role if missing
        admin_role = session.query(Role).filter(Role.role == "admin").first()
        if not admin_role:
            admin_role = Role(
                role="admin",
                fleet_permission='*',
                driver_permission='*',
                trips_permission='*',
                fuel_expense_permission='*',
                maintenance_permission='*',
                analytics_permission='*',
            )
            session.add(admin_role)
            session.commit()
            session.refresh(admin_role)

        # create admin user if missing
        existing = session.query(User).filter(User.username == admin_username).first()
        if not existing:
            hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = User(username=admin_username, password=hashed, role=admin_role.id)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                # if commit fails, ignore; user may have been created concurrently

import uuid
import bcrypt

from datetime import datetime, timedelta
from typing import Union, Literal
from fastapi import HTTPException


from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError


from .database import get_db, SessionLocal


from .model import BaseModel, User, Role, Vehicle, Driver, Trip, MaintenanceLog, FuelLog, Expense


class UserDAO:
    @classmethod
    def create_user(cls, db, data: dict):
        hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
        # assign role_id to the `role_id` column
        new_user = User(username=data["username"], password=hashed_password.decode('utf-8'), role_id=data["role_id"])
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Username already exists")

    @classmethod
    def authenticate_user(cls, db, credentials: dict):
        """Authenticate a user by username and password."""
        user = cls.get_user_by_username(db, credentials["username"])
        if not user:
            return {"error": "Invalid username", "status_code": 401, "message": "Invalid credentials"}
        if user and bcrypt.checkpw(credentials["password"].encode('utf-8'), user.password.encode('utf-8')):
            user.login_attempts = 0
            db.commit() 
            return user
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.is_locked = True
        db.add(user)
        db.commit()
        if user.is_locked:
            return {"error": "Account locked due to multiple failed login attempts", "status_code": 403, "message": "Account locked"}
        return {"error": "Invalid password", "status_code": 401, "message": "Invalid credentials"}

    

    @classmethod
    def get_user_by_username(cls, db, username: str):
        """Return a User by username or None."""
        return db.query(User).filter(User.username == username).first()

    @classmethod
    def get_user_by_id(cls, db, user_id: int):
        """Return a User by ID or None."""
        return db.query(User).filter(User.id == user_id).first()

    @classmethod
    def update_user(cls, db, user_id: int, data: dict):
        """Update a User by ID."""
        user = cls.get_user_by_id(db, user_id)
        if user:
            for key, value in data.items():
                if key == "password" and value:
                    value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    @classmethod
    def delete_user(cls, db, user_id: int):
        """Delete a User by ID."""
        user = cls.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

class RoleDAO:
    @classmethod
    def create_role(cls, db, data: dict):
        new_role = Role(**data)
        db.add(new_role)
        try:
            db.commit()
            db.refresh(new_role)
            return new_role
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Role already exists")

    @classmethod
    def get_role_by_id(cls, db, role_id: int):
        """Return a Role by ID or None."""
        return db.query(Role).filter(Role.id == role_id).first()

    @classmethod
    def get_role_by_name(cls, db, role: str):
        """Return a Role by name or None."""
        return db.query(Role).filter(Role.role == role).first()

    @classmethod
    def update_role(cls, db, role_id: int, data: dict):
        """Update a Role by ID."""
        role = cls.get_role_by_id(db, role_id)
        if role:
            for key, value in data.items():
                setattr(role, key, value)
            db.commit()
            db.refresh(role)
        return role

    @classmethod
    def delete_role(cls, db, role_id: int):
        """Delete a Role by ID."""
        role = cls.get_role_by_id(db, role_id)
        if role:
            db.delete(role)
            db.commit()
            return True
        return False

class VehicleDAO:

    @classmethod
    def create_vehicle(cls, db, data: dict):
        new_vehicle = Vehicle(**data)
        db.add(new_vehicle)
        try:
            db.commit()
            db.refresh(new_vehicle)
            return new_vehicle
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Vehicle with this registration number already exists")
    
    @classmethod
    def get_vehicle_by_id(cls, db, vehicle_id: int):
        """Return a Vehicle by ID or None."""
        return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    @classmethod
    def filter_vehicles(cls, db, filters: dict):
        """Filter vehicles based on provided criteria."""
        query = db.query(Vehicle)
        for key, value in filters.items():
            if hasattr(Vehicle, key):
                query = query.filter(getattr(Vehicle, key) == value)
        return query.all()

    

    @classmethod
    def update_vehicle(cls, db, vehicle_id: int, data: dict):
        """Update a Vehicle by ID."""
        vehicle = cls.get_vehicle_by_id(db, vehicle_id)
        if vehicle:
            for key, value in data.items():
                setattr(vehicle, key, value)
            db.commit()
            db.refresh(vehicle)
        return vehicle

    @classmethod
    def delete_vehicle(cls, db, vehicle_id: int):
        """Delete a Vehicle by ID."""
        vehicle = cls.get_vehicle_by_id(db, vehicle_id)
        if vehicle:
            db.delete(vehicle)
            db.commit()
            return True
        return False


class DriverDAO:
    @classmethod
    def create_driver(cls, db, data: dict):
        new_driver = Driver(**data)
        db.add(new_driver)
        try:
            db.commit()
            db.refresh(new_driver)
            return new_driver
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Driver with this license number already exists")
        
    @classmethod
    def get_driver_by_id(cls, db, driver_id: int):
        """Return a Driver by ID or None."""
        return db.query(Driver).filter(Driver.id == driver_id).first()

    @classmethod
    def filter_drivers(cls, db, filters: dict):
        """Filter drivers based on provided criteria."""
        query = db.query(Driver)
        for key, value in filters.items():
            if hasattr(Driver, key):
                query = query.filter(getattr(Driver, key) == value)
        return query.all()

    @classmethod
    def update_driver(cls, db, driver_id: int, data: dict):
        """Update a Driver by ID."""
        driver = cls.get_driver_by_id(db, driver_id)
        if driver:
            for key, value in data.items():
                setattr(driver, key, value)
            db.commit()
            db.refresh(driver)
        return driver

    @classmethod
    def delete_driver(cls, db, driver_id: int):
        """Delete a Driver by ID."""
        driver = cls.get_driver_by_id(db, driver_id)
        if driver:
            db.delete(driver)
            db.commit()
            return True
        return False

class TripDAO:
    @classmethod
    def create_trip(cls, db, data: dict):
        new_trip = Trip(**data)
        db.add(new_trip)
        try:
            db.commit()
            db.refresh(new_trip)
            return new_trip
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Trip creation failed due to integrity error")  
    
    @classmethod
    def get_trip_by_id(cls, db, trip_id: int):
        """Return a Trip by ID or None."""
        return db.query(Trip).filter(Trip.id == trip_id).first()

    @classmethod
    def filter_trips(cls, db, filters: dict):
        """Filter trips based on provided criteria."""
        query = db.query(Trip)
        for key, value in filters.items():
            if hasattr(Trip, key):
                query = query.filter(getattr(Trip, key) == value)
        return query.all()

    @classmethod
    def update_trip(cls, db, trip_id: int, data: dict):
        """Update a Trip by ID."""
        trip = cls.get_trip_by_id(db, trip_id)
        if trip:
            for key, value in data.items():
                setattr(trip, key, value)
            db.commit()
            db.refresh(trip)
        return trip

    @classmethod
    def delete_trip(cls, db, trip_id: int):
        """Delete a Trip by ID."""
        trip = cls.get_trip_by_id(db, trip_id)
        if trip:
            db.delete(trip)
            db.commit()
            return True
        return False

class MaintenanceLogDAO:
    @classmethod
    def create_maintenance_log(cls, db, data: dict):
        new_log = MaintenanceLog(**data)
        db.add(new_log)
        try:
            db.commit()
            db.refresh(new_log)
            return new_log
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Maintenance log creation failed due to integrity error")

    @classmethod
    def get_maintenance_log_by_id(cls, db, log_id: int):
        """Return a MaintenanceLog by ID or None."""
        return db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()

    @classmethod    
    def filter_maintenance_logs(cls, db, filters: dict):
        """Filter maintenance logs based on provided criteria."""
        query = db.query(MaintenanceLog)
        for key, value in filters.items():
            if hasattr(MaintenanceLog, key):
                query = query.filter(getattr(MaintenanceLog, key) == value)
        return query.all()

    @classmethod
    def update_maintenance_log(cls, db, log_id: int, data: dict):
        """Update a MaintenanceLog by ID."""
        log = cls.get_maintenance_log_by_id(db, log_id)
        if log:
            for key, value in data.items():
                setattr(log, key, value)
            db.commit()
            db.refresh(log)
        return log

    @classmethod
    def delete_maintenance_log(cls, db, log_id: int):
        """Delete a MaintenanceLog by ID."""
        log = cls.get_maintenance_log_by_id(db, log_id)
        if log:
            db.delete(log)
            db.commit()
            return True
        return False
    

class FuelLogDAO:
    @classmethod
    def create_fuel_log(cls, db, data: dict):
        new_log = FuelLog(**data)
        db.add(new_log)
        try:
            db.commit()
            db.refresh(new_log)
            return new_log
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Fuel log creation failed due to integrity error")

    @classmethod
    def get_fuel_log_by_id(cls, db, log_id: int):
        """Return a FuelLog by ID or None."""
        return db.query(FuelLog).filter(FuelLog.id == log_id).first()

    @classmethod    
    def filter_fuel_logs(cls, db, filters: dict):
        """Filter fuel logs based on provided criteria."""
        query = db.query(FuelLog)
        for key, value in filters.items():
            if hasattr(FuelLog, key):
                query = query.filter(getattr(FuelLog, key) == value)
        return query.all()

    @classmethod
    def update_fuel_log(cls, db, log_id: int, data: dict):
        """Update a FuelLog by ID."""
        log = cls.get_fuel_log_by_id(db, log_id)
        if log:
            for key, value in data.items():
                setattr(log, key, value)
            db.commit()
            db.refresh(log)
        return log

    @classmethod
    def delete_fuel_log(cls, db, log_id: int):
        """Delete a FuelLog by ID."""
        log = cls.get_fuel_log_by_id(db, log_id)
        if log:
            db.delete(log)
            db.commit()
            return True
        return False


class ExpenseDAO:
    @classmethod
    def create_expense(cls, db, data: dict):
        new_expense = Expense(**data)
        db.add(new_expense)
        try:
            db.commit()
            db.refresh(new_expense)
            return new_expense
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Expense creation failed due to integrity error")

    @classmethod
    def get_expense_by_id(cls, db, expense_id: int):
        """Return an Expense by ID or None."""
        return db.query(Expense).filter(Expense.id == expense_id).first()

    @classmethod    
    def filter_expenses(cls, db, filters: dict):
        """Filter expenses based on provided criteria."""
        query = db.query(Expense)
        for key, value in filters.items():
            if hasattr(Expense, key):
                query = query.filter(getattr(Expense, key) == value)
        return query.all()

    @classmethod
    def update_expense(cls, db, expense_id: int, data: dict):
        """Update an Expense by ID."""
        expense = cls.get_expense_by_id(db, expense_id)
        if expense:
            for key, value in data.items():
                setattr(expense, key, value)
            db.commit()
            db.refresh(expense)
        return expense

    @classmethod
    def delete_expense(cls, db, expense_id: int):
        """Delete an Expense by ID."""
        expense = cls.get_expense_by_id(db, expense_id)
        if expense:
            db.delete(expense)
            db.commit()
            return True
        return False


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
            user = User(username=admin_username, password=hashed, role_id=admin_role.id)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                # if commit fails, ignore; user may have been created concurrently

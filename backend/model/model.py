from enum import Enum
from typing import List, Literal, Union

from .database import engine


from datetime import datetime
from datetime import timezone
from datetime import timedelta

from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, Date
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SQLEnum


Base = declarative_base()

# when the system time is not IST
# Define the offset for IST (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30)) # pass it as argument to now as datetime.now(IST)

def get_date():
    return datetime.now()

class VehicleStatusEnum(str, Enum):
    available = "available"
    on_trip = "on_trip"
    in_shop = "in_shop"
    retired = "retired"

class DriverStatusEnum(str, Enum):
    available = "available"
    on_trip = "on_trip"
    off_duty = "off_duty"
    suspended = "suspended"


class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    def __iter__(self):
        cols = self.__table__.columns.keys()[:-2]

        for col in cols:
            val = getattr(self, col)
            if type(val) in [str, datetime.date]:
                val = str(val)
            yield val


    def to_dict(self):
        cols = self.__table__.columns.keys()[:-2]
        
        d = {}
        for col in cols:
            val = getattr(self, col)
            if type(val) in [str, datetime.date]:
                val = str(val)
            d[col] = val
        return d

    def __repr__(self):
        return str(tuple(self))

# Users, Roles, Vehicles, Drivers, Trips, Maintenance Logs, Fuel Logs, Expenses

class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(Integer, ForeignKey("roles.id"), nullable=False)
    login_attempts = Column(Integer, default=0)
    is_locked = Column(Integer, default=0)  # 0 for unlocked, 1 for locked

class Role(BaseModel):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(50), unique=True, nullable=False)
    fleet_permission = Column(String(50), nullable=False) # */r/w/n
    driver_permission = Column(String(50), nullable=False) # 
    trips_permission = Column(String(50), nullable=False) # 
    fuel_expense_permission = Column(String(50), nullable=False) 
    maintenance_permission = Column(String(50), nullable=False)
    analytics_permission = Column(String(50), nullable=False) 
    

class Vehicle(BaseModel):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reistration_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    max_capacity = Column(Float, nullable=False)
    capacity_unit = Column(String(10), nullable=False)
    odometer_reading = Column(Float, nullable=False)
    acquisition_cost = Column(Float, nullable=False)
    status = Column(SQLEnum(VehicleStatusEnum), nullable=False)

class Driver(BaseModel):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    licence_number = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    license_expiry_date = Column(Date, nullable=False)
    contact_number = Column(String(15), nullable=False)
    safety_score = Column(Float, nullable=False)
    status = Column(SQLEnum(DriverStatusEnum), nullable=False)
    pass

class Trip(BaseModel):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    vehicle = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    cargo_weight = Column(Float, nullable=False)
    planned_distance = Column(Float, nullable=False) # in KM
    lifecycle_status = Column(String(50), nullable=False) # Draft → Dispatched → Completed → Cancelled.
    pass

class MaintenanceLog(BaseModel):
    __tablename__ = "maintenance_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    service_type = Column(String(100), nullable=False)
    cost = Column(Float, nullable=False)
    service_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False) # Active → Completed → Cancelled

class FuelLog(BaseModel):
    __tablename__ = "fuel_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    date = Column(Date, nullable=False)
    fuel_quantity = Column(Float, nullable=False)
    fuel_cost = Column(Float, nullable=False)


class Expense(BaseModel):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip = Column(Integer, ForeignKey("trips.id"), nullable=False)
    vehicle = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    expense_type = Column(String(100), nullable=False) # toll/miscellaneous/other
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)


def create_tables():
    Base.metadata.create_all(engine)

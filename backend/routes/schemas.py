from typing import Union

from sqlalchemy.dialects.postgresql import INET
from sqlalchemy import DateTime

from pydantic import BaseModel

class AuthModel(BaseModel):
    username: str
    password: str

class UserBase(BaseModel):
    username: str
    password: str
    role_id: int


class VehicleCreateModel(BaseModel):
    registration_number: str
    name: str
    type: str
    max_capacity: int
    capacity_unit: str
    odometer_reading: int
    acquisition_cost: float
    status: str

class RoleCreateModel(BaseModel):
    role: str
    fleet_permission: str
    driver_permission: str
    trips_permission: str
    fuel_expense_permission: str
    maintenance_permission: str
    analytics_permission: str
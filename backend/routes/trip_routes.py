    

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from model import get_db, TripDAO, Vehicle,  VehicleDAO, Trip, Driver, RoleDAO
from model.model import VehicleStatusEnum, DriverStatusEnum
from middleware import auth_middleware

from routes.schemas import VehicleCreateModel

trip_router = APIRouter(tags=["Trips"])

@trip_router.post("/trip", status_code=status.HTTP_201_CREATED)
def create_trip(trip_data: dict, db=Depends(get_db), auth=Depends(auth_middleware)):
    
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.trip_permission in ["*", "w"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    required = [
        "vehicle_id",
        "driver_id",
        "start_location",
        "end_location",
        "start_time",
        "end_time",
        "status",
    ]
    missing = [field for field in required if field not in trip_data]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required fields: {', '.join(missing)}")

    try:
        new_trip = TripDAO.create_trip(db, trip_data)
        return {"message": "Trip created successfully", "trip": new_trip.to_dict()}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
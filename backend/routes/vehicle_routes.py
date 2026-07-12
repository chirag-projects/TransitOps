from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from model import get_db, VehicleDAO, Vehicle, Trip, Driver, RoleDAO
from model.model import VehicleStatusEnum, DriverStatusEnum
from middleware import auth_middleware

from routes.schemas import VehicleCreateModel

vehicle_router = APIRouter(tags=["Vehicles"])

@vehicle_router.post("/vehicle", status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle_data: VehicleCreateModel, db=Depends(get_db), auth=Depends(auth_middleware)):
    
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.vehicle_permission in ["*", "w"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    required = [
        "registration_number",
        "name",
        "type",
        "max_capacity",
        "capacity_unit",
        "odometer_reading",
        "acquisition_cost",
        "status",
    ]
    missing = [field for field in required if field not in vehicle_data]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required fields: {', '.join(missing)}")

    try:
        new_vehicle = VehicleDAO.create_vehicle(db, vehicle_data)
        return {"message": "Vehicle created successfully", "vehicle": new_vehicle.to_dict()}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@vehicle_router.get("/vehicle/dashboard", status_code=status.HTTP_200_OK)
def get_vehicle_dashboard(
    vehicle_type: Optional[str] = None,
    vehicle_status: Optional[str] = None,
    region: Optional[str] = None,
    db=Depends(get_db),
    auth=Depends(auth_middleware),
):
    
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.vehicle_permission in ["*", "w", "r"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    valid_vehicle_statuses = [status.value for status in VehicleStatusEnum]
    if vehicle_status and vehicle_status not in valid_vehicle_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid vehicle_status. Valid values: {', '.join(valid_vehicle_statuses)}",
        )

    vehicle_query = db.query(Vehicle)
    if vehicle_type:
        vehicle_query = vehicle_query.filter(Vehicle.type == vehicle_type)
    if vehicle_status:
        vehicle_query = vehicle_query.filter(Vehicle.status == vehicle_status)
    if region:
        if not hasattr(Vehicle, "region"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region filtering is unavailable because the Vehicle model has no region field.",
            )
        vehicle_query = vehicle_query.filter(getattr(Vehicle, "region") == region)

    total_vehicles = vehicle_query.count()
    available_vehicles = vehicle_query.filter(Vehicle.status == VehicleStatusEnum.available).count()
    vehicles_in_maintenance = vehicle_query.filter(Vehicle.status == VehicleStatusEnum.in_shop).count()
    vehicles_on_trip = vehicle_query.filter(Vehicle.status == VehicleStatusEnum.on_trip).count()
    active_vehicles = vehicle_query.filter(Vehicle.status != VehicleStatusEnum.retired).count()

    vehicle_ids_subquery = vehicle_query.with_entities(Vehicle.id).subquery()

    if total_vehicles > 0:
        active_trips_query = db.query(Trip).filter(
            Trip.lifecycle_status == "Dispatched",
            Trip.vehicle_id.in_(vehicle_ids_subquery),
        )
        pending_trips_query = db.query(Trip).filter(
            Trip.lifecycle_status == "Draft",
            Trip.vehicle_id.in_(vehicle_ids_subquery),
        )
        active_trips = active_trips_query.count()
        pending_trips = pending_trips_query.count()

        drivers_on_duty = db.query(Driver).join(Trip, Driver.id == Trip.driver_id).filter(
            Driver.status == DriverStatusEnum.on_trip,
            Trip.lifecycle_status == "Dispatched",
            Trip.vehicle_id.in_(vehicle_ids_subquery),
        ).distinct(Driver.id).count()
    else:
        active_trips = 0
        pending_trips = 0
        drivers_on_duty = 0

    fleet_utilization = 0.0
    if total_vehicles:
        fleet_utilization = round((vehicles_on_trip / total_vehicles) * 100, 2)

    return {
        "dashboard": {
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "available_vehicles": available_vehicles,
            "vehicles_in_maintenance": vehicles_in_maintenance,
            "active_trips": active_trips,
            "pending_trips": pending_trips,
            "drivers_on_duty": drivers_on_duty,
            "fleet_utilization": fleet_utilization,
            "filters": {
                "vehicle_type": vehicle_type,
                "vehicle_status": vehicle_status,
                "region": region,
            },
        }
    }


@vehicle_router.put("/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
def update_vehicle(vehicle_id: int, vehicle_data: dict, db=Depends(get_db), auth=Depends(auth_middleware)):
    
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.vehicle_permission in ["*", "w"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    

    vehicle = VehicleDAO.get_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return VehicleDAO.update_vehicle(db, vehicle_id, vehicle_data)


@vehicle_router.delete("/vehicle/{vehicle_id}", status_code=status.HTTP_200_OK)
def delete_vehicle(vehicle_id: int, db=Depends(get_db), auth=Depends(auth_middleware)):
    vehicle = VehicleDAO.get_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    try:
        VehicleDAO.delete_vehicle(db, vehicle)
        return {"message": "Vehicle deleted successfully"}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
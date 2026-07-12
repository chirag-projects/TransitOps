from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status

from model import get_db, DriverDAO, RoleDAO
from model import Driver
from middleware import auth_middleware

driver_router = APIRouter(tags=["Drivers"])

@driver_router.post("/drivers", status_code=status.HTTP_201_CREATED)
def create_driver(driver_data: dict, db=Depends(get_db), auth=Depends(auth_middleware)):
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.driver_permission in ["*", "w"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    required = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "license_number",
        "license_expiry_date",
        "status",
    ]
    missing = [field for field in required if field not in driver_data]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required fields: {', '.join(missing)}")

    try:
        new_driver = DriverDAO.create_driver(db, driver_data)
        return {"message": "Driver created successfully", "driver": new_driver.to_dict()}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    
@driver_router.get("/driver/{driver_id}", status_code=status.HTTP_200_OK)
def get_driver(driver_id: int, db=Depends(get_db), auth=Depends(auth_middleware)):
    """Get a driver by ID."""
    
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.driver_permission in ["*", "w", "r"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    

    driver = DriverDAO.get_driver_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"driver": driver.to_dict()}

@driver_router.put("/driver/{driver_id}", status_code=status.HTTP_200_OK)
def update_driver(driver_id: int, driver_data: dict, db=Depends(get_db), auth=Depends(auth_middleware)):
    
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.driver_permission in ["*", "w"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    driver = DriverDAO.get_driver_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return DriverDAO.update_driver(db, driver_id, driver_data)

@driver_router.delete("/driver/{driver_id}", status_code=status.HTTP_200_OK)
def delete_driver(driver_id: int, db=Depends(get_db), auth=Depends(auth_middleware)):
    role_id = auth["role_id"]
    role = RoleDAO.get_role_by_id(db, role_id)
    if not (role and role.driver_permission in ["*", "w"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    driver = DriverDAO.get_driver_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    DriverDAO.delete_driver(db, driver_id)
    return {"message": "Driver deleted successfully"}
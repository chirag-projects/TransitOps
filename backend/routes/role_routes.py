from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from model import get_db, RoleDAO
from model import Role
from middleware import admin_middleware

from routes.schemas import RoleCreateModel

role_router = APIRouter(tags=["Roles"])

@role_router.post("/role", status_code=status.HTTP_201_CREATED)
def create_role(role_data: RoleCreateModel, db=Depends(get_db), auth=Depends(admin_middleware)):
    required = ["role"]
    missing = [field for field in required if field not in role_data]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required fields: {', '.join(missing)}")

    try:
        new_role = RoleDAO.create_role(db, role_data)
        return {"message": "Role created successfully", "role": new_role.to_dict()}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@role_router.get("/roles", status_code=status.HTTP_200_OK)
def get_roles(db=Depends(get_db), auth=Depends(admin_middleware)):  
    try:
        roles = RoleDAO.get_all_roles(db)
        return {"roles": [role.to_dict() for role in roles]}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    
@role_router.get("/role/{role_id}", status_code=status.HTTP_200_OK)
def get_role(role_id: int, db=Depends(get_db), auth=Depends(admin_middleware)):
    try:
        role = RoleDAO.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return {"role": role.to_dict()}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))   

@role_router.put("/role/{role_id}", status_code=status.HTTP_200_OK)
def update_role(role_id: int, role_data: RoleCreateModel, db=Depends(get_db), auth=Depends(admin_middleware)):
    try:
        role = RoleDAO.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        updated_role = RoleDAO.update_role(db, role_id, role_data)
        return {"message": "Role updated successfully", "role": updated_role.to_dict()}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))       

@role_router.delete("/role/{role_id}", status_code=status.HTTP_200_OK)
def delete_role(role_id: int, db=Depends(get_db), auth=Depends(admin_middleware)):
    try:
        role = RoleDAO.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        RoleDAO.delete_role(db, role_id)
        return {"message": "Role deleted successfully"}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    

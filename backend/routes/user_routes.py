from model import get_db

from fastapi import Request
from fastapi import APIRouter, HTTPException, status, Depends

from middleware import auth_middleware, admin_middleware


from model import User
from model import UserDAO

user_router = APIRouter(tags=["User"])

@user_router.post("/user", status_code=status.HTTP_201_CREATED)
def create_user(user_data: dict, db=Depends(get_db), auth=Depends(admin_middleware)):
    """Create a new user."""
    try:
        new_user = UserDAO.create_user(db, user_data)
        return {"message": "User created successfully", "user": new_user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@user_router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: int, db=Depends(get_db), auth=Depends(admin_middleware)):
    """Get a user by ID."""
    user = UserDAO.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


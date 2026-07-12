from model import get_db

from fastapi import Request
from fastapi import APIRouter, HTTPException, status, Depends
from middleware import auth_middleware, admin_middleware, generate_jwt_token

from .schemas import AuthModel

from model import User
from model import UserDAO

auth_router = APIRouter(tags=["Auth"])

@auth_router.post("/login", status_code=status.HTTP_200_OK)
def login_user(credentials: dict, db=Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    try:
        user = UserDAO.authenticate_user(db, credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = generate_jwt_token(user)
        return {"token": token, "user": user.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


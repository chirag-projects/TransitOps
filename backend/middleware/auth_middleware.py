import jwt
import os
from dotenv import load_dotenv
from fastapi import Header, Depends, HTTPException 

from datetime import datetime, timedelta

load_dotenv()

jwt_secret_key = os.getenv("JWT_SECRET_KEY", "e9afd0235f83860580fe93c0")  # Default value if not set in .env

def auth_middleware(x_auth_token=Header()):
    try:
        # get the user token from headers.
        if not x_auth_token:
            raise HTTPException(401, "No auth token, access denied.")
        #
        # decode the token
        verified_token = jwt.decode(x_auth_token, jwt_secret_key, algorithms=["HS256"])

        if not verified_token:
            raise HTTPException(401, "Unauthorized")

        # get the id from the token
        uid = verified_token.get("id")
        role = verified_token.get("role")
        return {"id": uid, "role": role, "token": x_auth_token}
    except jwt.PyJWTError:
        raise HTTPException(401, "Unauthorized")


def admin_middleware(auth=Depends(auth_middleware)):
    if auth.get("role") != "admin":
        raise HTTPException(403, "Forbidden: Admins only.")
    return auth

def generate_jwt_token(user):
    """Generate a JWT token for the authenticated user."""

    role_name = None
    if getattr(user, "role", None) is not None and hasattr(user.role, "role"):
        role_name = user.role.role
    

    if not role_name:
        raise ValueError("Unable to determine user role for JWT generation")


    payload = {
        "id": user.id,
        "username": user.username,
        "role": role_name,
        "role_id": user.role_id,
        "exp": datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    }

    print(payload)
    token = jwt.encode(payload, jwt_secret_key, algorithm="HS256")
    return token
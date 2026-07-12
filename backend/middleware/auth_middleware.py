import jwt
import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException


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
        return {"id": uid, "token": x_auth_token}
    except jwt.PyJWTError:
        raise HTTPException(401, "Unauthorized")

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


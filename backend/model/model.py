from typing import List, Literal, Union

from .database import engine


from datetime import datetime
from datetime import timezone
from datetime import timedelta

from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, Date
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import JSONB



Base = declarative_base()

# when the system time is not IST
# Define the offset for IST (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30)) # pass it as argument to now as datetime.now(IST)

def get_date():
    return datetime.now()

def create_tables():
    Base.metadata.create_all(engine)

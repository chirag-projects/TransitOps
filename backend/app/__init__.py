from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, user_router, vehicle_router, driver_router, trip_router
from routes import role_router

from model.model import create_tables


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.24.5.56:8080/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(vehicle_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(driver_router, prefix="/api/v1")
app.include_router(trip_router, prefix="/api/v1")

create_tables()

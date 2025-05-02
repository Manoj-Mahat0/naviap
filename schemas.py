from typing import Optional
from pydantic import BaseModel

# ----------------- Vehicle Registration -----------------
class VehicleRegister(BaseModel):
    imei_number: str
    vehicle_number: str
    vehicle_type: str

class VehicleResponse(BaseModel):
    id: int
    vehicle_number: str
    vehicle_type: str
    imei_id: int

    class Config:
        orm_mode = True

# ----------------- IMEI Login -----------------
class IMEILogin(BaseModel):
    imei_number: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# ----------------- Driver Management -----------------
class DriverCreate(BaseModel):
    name: str
    phone: str
    license_number: str
    vehicle_id: int

class DriverResponse(BaseModel):
    id: int
    name: str
    phone: str
    license_number: str
    vehicle_id: int

    class Config:
        orm_mode = True

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None

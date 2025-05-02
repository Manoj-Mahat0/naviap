from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine  # ✅ FIXED: import engine from database
import models, schemas
from auth import create_access_token, get_current_imei
import random

app = FastAPI()

# Create DB tables
models.Base.metadata.create_all(bind=engine)

@app.post("/register", summary="Register a vehicle")
def register_vehicle(data: schemas.VehicleRegister, db: Session = Depends(get_db)):
    # Find or create IMEI
    imei = db.query(models.IMEI).filter(models.IMEI.imei_number == data.imei_number).first()
    if not imei:
        imei = models.IMEI(imei_number=data.imei_number)
        db.add(imei)
        db.commit()
        db.refresh(imei)

    # ✅ Check for duplicate vehicle under same IMEI
    existing_vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_number == data.vehicle_number,
        models.Vehicle.imei_id == imei.id
    ).first()

    if existing_vehicle:
        raise HTTPException(status_code=400, detail="Vehicle already registered under this IMEI")

    # Register vehicle
    vehicle = models.Vehicle(
        vehicle_number=data.vehicle_number,
        vehicle_type=data.vehicle_type,
        imei_id=imei.id
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return {"message": "Vehicle registered successfully", "vehicle_id": vehicle.id}


@app.post("/login", response_model=schemas.TokenResponse, summary="Login with IMEI")
def login_imei(data: schemas.IMEILogin, db: Session = Depends(get_db)):
    imei = db.query(models.IMEI).filter(models.IMEI.imei_number == data.imei_number).first()
    if not imei:
        raise HTTPException(status_code=401, detail="IMEI not found")

    token = create_access_token(data={"sub": imei.imei_number})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def read_imei_info(imei_number: str = Depends(get_current_imei)):
    return {"imei_number": imei_number}


@app.get("/vehicles", response_model=list[schemas.VehicleResponse], summary="Get all vehicles")
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles

@app.get("/vehicles/by-imei/{imei_number}", response_model=list[schemas.VehicleResponse])
def get_vehicles_by_imei(imei_number: str, db: Session = Depends(get_db)):
    imei = db.query(models.IMEI).filter(models.IMEI.imei_number == imei_number).first()
    if not imei:
        raise HTTPException(status_code=404, detail="IMEI not found")
    return imei.vehicles


@app.get("/vehicles/{vehicle_id}", response_model=schemas.VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@app.post("/add-driver", response_model=schemas.DriverResponse)
def add_driver(
    driver: schemas.DriverCreate,
    db: Session = Depends(get_db),
    imei_number: str = Depends(get_current_imei)  # ✅ Protects this route
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == driver.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    existing = db.query(models.Driver).filter(models.Driver.vehicle_id == driver.vehicle_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="This vehicle already has a driver.")

    new_driver = models.Driver(**driver.dict())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver


@app.put("/update-driver/{driver_id}", response_model=schemas.DriverResponse)
def update_driver(
    driver_id: int,
    updated_driver: schemas.DriverUpdate,
    db: Session = Depends(get_db),
    imei_number: str = Depends(get_current_imei)  # 🔐 Token-protected
):
    # Fetch the driver
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Update fields if provided
    for field, value in updated_driver.dict(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)

    return driver

@app.get("/vehicle-status/{vehicle_id}")
def get_vehicle_status(vehicle_id: int, imei_number: str = Depends(get_current_imei)):
    # Optionally: Validate the vehicle belongs to this IMEI
    # (left simple for now)

    # Generate random data
    lat = round(random.uniform(22.0, 28.0), 6)
    lng = round(random.uniform(70.0, 90.0), 6)
    battery = random.randint(20, 100)  # in percentage
    signal = random.choice(["Excellent", "Good", "Fair", "Poor"])

    return {
        "vehicle_id": vehicle_id,
        "location": {
            "latitude": lat,
            "longitude": lng
        },
        "battery": f"{battery}%",
        "signal_strength": signal
    }


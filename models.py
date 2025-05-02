from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from database import Base

class IMEI(Base):
    __tablename__ = "imeis"
    id = Column(Integer, primary_key=True, index=True)
    imei_number = Column(String, unique=True, index=True)
    vehicles = relationship("Vehicle", back_populates="imei")


class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    license_number = Column(String, unique=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), unique=True)

    vehicle = relationship("Vehicle", back_populates="driver")

    __table_args__ = (
        UniqueConstraint('vehicle_id', name='uq_driver_vehicle'),
    )


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String, index=True)
    vehicle_type = Column(String)
    imei_id = Column(Integer, ForeignKey("imeis.id"))

    imei = relationship("IMEI", back_populates="vehicles")
    driver = relationship("Driver", back_populates="vehicle", uselist=False)  # one-to-one


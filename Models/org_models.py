from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True, index=True)
    org_name = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_info = Column(String, nullable=False)
    bio = Column(String, nullable=True)

class GeoTag(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    venue: str
    geo_tag: GeoTag

class Organization_details(BaseModel):
    org_name: str
    location:Location
    contact_info: str
    bio: Optional[str]=""


class OTPVerification(BaseModel):
    email: str
    otp_code: str
    username: str
    password: str
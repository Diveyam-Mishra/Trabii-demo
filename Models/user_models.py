from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    is_admin = Column(Boolean, default=False)
    works_at = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    contact_no = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic models
class UserBase(BaseModel):
    email: str
    username: str
    password: str
    is_admin: Optional[bool] = False
    works_at: Optional[str] = None
    avatar: Optional[str] = None
    contact_no: Optional[str] = None

class UserResponse(BaseModel):
    email: EmailStr
    username: str
    is_admin: bool
    works_at: Optional[str]
    avatar: Optional[str]
    contact_no: Optional[str]
    created_at: datetime
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_admin: Optional[bool] = False
    works_at: Optional[str] = None
    avatar: Optional[str] = None
    contact_no: Optional[str] = None

class UserLogin(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

class SuccessResponse(BaseModel):
    message: str
    token: Optional[str] =""
    success: bool

    class Config:
        orm_mode = True


class DeleteUserAfterCheckingPass(BaseModel):
    password: str


class NoSQLUser(BaseModel):
    id: int
    personality_tags: Optional[str] = None
    cost: Optional[float] = None
    range: Optional[str] = None
    friends: List[int] = []


class OTP(Base):
    __tablename__ = 'otps-try'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

def is_otp_expired(otp_entry):
    if otp_entry.created_at.tzinfo is None:
        otp_entry.created_at = otp_entry.created_at.replace(tzinfo=timezone.utc)
    
    expiry_time = otp_entry.created_at + timedelta(minutes=10)
    current_time = datetime.now(timezone.utc)
    
    return current_time > expiry_time

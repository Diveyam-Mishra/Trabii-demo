# main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func ,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta , timezone
from passlib.context import CryptContext
import jwt
import random
import asyncio
from otp import send_otp_email
from Controllers.Auth import (create_user, get_user, get_current_user, get_user_by_email, get_user_by_username, settings, get_db, engine, JWT_SECRET)
from Models.user_models import (
    DeleteUserAfterCheckingPass,
    SuccessResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    OTP,
    is_otp_expired
)
from config import *
from Models.org_models import ( OTPVerification)
from fastapi.middleware.cors import CORSMiddleware
from Controllers.add_org import router as organization_router

app = FastAPI(title="Backend with MongoDB and SQL")

origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongoURI)
database = client.TrabiiBackendTest
collection = database.users

Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

class OTP(Base):
    __tablename__ = 'otps'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    otp_code = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True, index=True)
    org_name = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_info = Column(String, nullable=False)
    bio = Column(String, nullable=True)


# Initialize SQL database
def init_db():
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup_event():
    init_db()  # Initialize SQL database
    print(connstring)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/user/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session=Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user:
        return db_user
    raise HTTPException(404, f"User with ID {user_id} not found")


@app.post("/api/user/", response_model=UserResponse)
def add_user(user: UserCreate, db: Session=Depends(get_db)):
    db_user = create_user(db, user)
    return db_user


# Register a User
@app.post("/api/register/", response_model=SuccessResponse)
def register_user(user: UserCreate, db: Session=Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password
    
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    
    # Create new user
    new_user = create_user(db, user)

    # Generate JWT token
    token_data = {"user_id": new_user.id}
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

    return {"message":"User Created Successfully", "token":token, "success": True}


# Authenticate a User
@app.post("/api/login", response_model=SuccessResponse)
def login_user(login_data: UserLogin, db: Session=Depends(get_db)):
    if login_data.email:
        user = get_user_by_email(db, login_data.email)
    elif login_data.username:
        user = get_user_by_username(db, login_data.username)
    else:
        raise HTTPException(status_code=400, detail="Email or username is required")

    if not user:
        return SuccessResponse(message="User Not Found", token="", success=False)

    if not pwd_context.verify(login_data.password, user.password):
        return SuccessResponse(message="Invalid Credentials", token="", success=False)

    # Generate JWT token
    token_data = {"user_id": user.id}
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

    return SuccessResponse(message="User Authenticated", token=token, success=True)


@app.get("/api/getuser")
def get_user_details(current_user: User=Depends(get_current_user)):
    # The user data is already fetched by get_current_user and assigned to current_user
    # Return user details without sensitive information
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "works_at": current_user.works_at,
        "avatar": current_user.avatar,
        "contact_no": current_user.contact_no,
        "created_at": current_user.created_at
    }
    return user_data


@app.post("/api/delete_user/")
def delete_user(delete_data: DeleteUserAfterCheckingPass, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    # Verify the provided password
    if not pwd_context.verify(delete_data.password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Delete the user
    db.delete(current_user)
    db.commit()
    
    return SuccessResponse(message="User deleted sucessfully", token="", success=True)
@app.post("/api/register/send-otp/", response_model=SuccessResponse)
def send_otp(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Generate OTP
    otp_code = random.randint(100000, 999999)
    
    # Send OTP email
    send_otp_email(user.email, otp_code)

    # Store OTP in the database
    otp_entry = OTP(email=user.email, otp_code=str(otp_code), created_at=datetime.utcnow())
    db.add(otp_entry)
    db.commit()
    db.refresh(otp_entry)

    return {"message": "OTP Sent. Check your email.", "success": True}

# Register a User Part 2: Verify OTP and Complete Registration
@app.post("/api/register/verify-otp/", response_model=SuccessResponse)
def verify_otp(otp_data: OTPVerification , db: Session = Depends(get_db)):
    email = otp_data.email
    otp_code = otp_data.otp_code

    otp_entry = db.query(OTP).filter(OTP.email == email).first()
    if not otp_entry or otp_entry.otp_code != otp_code or is_otp_expired(otp_entry):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Delete OTP entry after successful verification
    db.delete(otp_entry)
    db.commit()

    # Hash the password
    hashed_password = pwd_context.hash(otp_data.password)

    # Creating the user after OTP verification
    user_create = UserCreate(username=otp_data.username, email=email, password=hashed_password)
    new_user = create_user(db, user_create)

    # Generate JWT token
    token_data = {"user_id": new_user.id}
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

    return {"message": "User Created Successfully.", "token": token, "success": True}


app.include_router(organization_router)
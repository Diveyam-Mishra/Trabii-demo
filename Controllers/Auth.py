from sqlalchemy.orm import Session
from Models.user_models import User, UserBase, UserCreate, UserResponse, NoSQLUser, SuccessResponse, UserLogin, DeleteUserAfterCheckingPass
from jose import JWTError
from fastapi import HTTPException, Depends
import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import *
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM

def get_current_user(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
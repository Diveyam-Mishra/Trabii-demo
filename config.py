from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    mongoURI: str
    sqlURI: str
    endpoint:str
    accesskey:str
    sender_email:str

    class Config:
        env_file = ".env"

settings = Settings()
SQLALCHEMY_DATABASE_URL = settings.sqlURI
JWT=settings.JWT_SECRET
expire_time=settings.ACCESS_TOKEN_EXPIRE_MINUTES
accesskey=settings.accesskey
endpoint=settings.endpoint
connstring="endpoint="+endpoint+";"+"accesskey="+accesskey
senderMailAddress=settings.sender_email

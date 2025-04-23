from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_DB: str = "DG"
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: list[str] = ["*"]
    SERVER_PORT: Optional[int] = 5892
    PROJECT_NAME: str = "Cafe Dolce Goose API"
    VERSION: str = "DEV 1.2.0 | Build 23.04.2025"
    ROOTUSER_PASSWORD: Optional[str] ="root"
    ACCOUNT_ID: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()

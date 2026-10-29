from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://vidyaverify_user:change_me_in_production@localhost:5432/vidyaverify"

    # JWT
    SECRET_KEY: str = "dev_secret_key_change_in_production_32ch"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 10

    # Environment
    ENV: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()

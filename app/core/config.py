# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Keep existing fields
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Banking Disputes Resolution System"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./disputes.db"

    # Add this to accept Google API key from environment
    GOOGLE_API_KEY: str = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

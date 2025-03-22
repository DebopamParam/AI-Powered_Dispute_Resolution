# app/core/ai_config.py
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    # Use the same environment variable name
    GOOGLE_API_KEY: str  # No default value

    # Rest of your existing AI config
    GEMINI_MODEL: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1024
    MAX_RETRIES: int = 2
    RETRY_DELAY: int = 4

    class Config:
        env_file = ".env"
        extra = "ignore"


ai_settings = AISettings()

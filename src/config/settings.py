"""
Configuration settings for the Paryavaran application.
Loads and validates environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and/or .env file.
    """
    SECRET_KEY: str = "supersecretkeyreplaceinproduction1234567890abcdef"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./paryavaran.db"
    ENV: str = "development"

    # Configuration to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate settings to be imported across the application
settings = Settings()

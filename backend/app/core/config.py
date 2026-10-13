"""
Configuration module for JurisLink backend.
Loads environment variables and provides centralized settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "jurislink"
    
    # JWT
    JWT_SECRET: str = "dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    BACKEND_PORT: int = 8000
    BACKEND_HOST: str = "0.0.0.0"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

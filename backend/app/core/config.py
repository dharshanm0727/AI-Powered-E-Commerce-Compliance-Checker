import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Metrology E-Commerce Compliance Checker"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "e_commerce_compliance_checker_super_secret_jwt_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ]

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "compliance_db"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/compliance_db"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/compliance_db"

    # Celery & Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # AI Configuration
    LLM_PROVIDER: str = "mock"  # mock, gemini, openai
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-pro"

    # Storage
    UPLOAD_DIR: str = "./uploads"
    OCR_CACHE_DIR: str = "./ocr_cache"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()

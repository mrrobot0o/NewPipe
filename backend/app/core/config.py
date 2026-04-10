"""
Teresa Configuration Module
Centralized settings with environment variable support.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Teresa"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # LLM Configuration (OpenAI-compatible)
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL_NAME: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # Agent defaults
    MAX_AGENTS: int = 10000
    AGENT_INTERACTION_ROUNDS: int = 40
    AGENT_PERSONALITY_DEPTH: int = 5  # number of personality dimensions

    # Memory
    MEMORY_BACKEND: str = "qdrant"  # qdrant, pinecone, or chroma
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "teresa_memory"

    # Database
    DATABASE_URL: str = "postgresql://teresa:teresa@localhost:5432/teresa"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Simulation
    SIMULATION_WORKERS: int = 4
    SIMULATION_TIMEOUT: int = 300  # seconds
    SIMULATION_STREAM_INTERVAL: float = 0.5  # seconds between stream updates

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

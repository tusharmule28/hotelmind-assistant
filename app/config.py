import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Hotel Booking AI Assistant"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    CONFIDENCE_THRESHOLD: float = 0.65

    # Tenacity Retry Settings
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_MIN_WAIT_SECONDS: float = 1.0
    RETRY_MAX_WAIT_SECONDS: float = 4.0

    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./hotel_booking.db"

    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Sentence Transformer Settings
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", PROJECT_ROOT / "backend-django" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "rag-service"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    cors_allowed_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ALLOWED_ORIGINS",
    )
    document_storage_root: Path = Field(
        default=PROJECT_ROOT / "backend-django" / "media",
        alias="DOCUMENT_STORAGE_ROOT",
    )
    embedding_dimensions: int = Field(default=384, alias="EMBEDDING_DIMENSIONS")
    embedding_provider: str = Field(default="hash", alias="EMBEDDING_PROVIDER")
    llm_provider: str = Field(default="extractive", alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")
    openai_chat_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_CHAT_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    use_pgvector: bool = Field(default=False, alias="USE_PGVECTOR")
    chunk_token_size: int = Field(default=900, alias="CHUNK_TOKEN_SIZE")
    chunk_token_overlap: int = Field(default=120, alias="CHUNK_TOKEN_OVERLAP")
    retrieval_threshold: float = Field(default=0.18, alias="RETRIEVAL_THRESHOLD")
    retrieval_cache_ttl_seconds: int = Field(default=1200, alias="RETRIEVAL_CACHE_TTL_SECONDS")

    @property
    def is_database_configured(self) -> bool:
        return bool(self.database_url)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

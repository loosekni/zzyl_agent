from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ZZYL Agent"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./zzyl_agent.db"
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "claude-opus-4-8"
    llm_base_url: str | None = None
    llm_temperature: float = 0.2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()

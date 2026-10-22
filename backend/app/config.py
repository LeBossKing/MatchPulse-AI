"""Backend-only configuration, loaded independently of the working directory."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    frontend_origin: str = "http://localhost:5173"
    llm_provider: Literal["mock", "azure"] = "mock"
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_key: SecretStr | None = None

    @property
    def allowed_origins(self) -> list[str]:
        return list(
            dict.fromkeys(
                [
                    self.frontend_origin.rstrip("/"),
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

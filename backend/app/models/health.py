from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["matchpulse-api"] = "matchpulse-api"
    version: str
    environment: Literal["development", "test", "production"]

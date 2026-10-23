from typing import Literal

from app.models.common import ContractModel


class HealthResponse(ContractModel):
    status: Literal["ok"] = "ok"
    service: Literal["matchpulse-api"] = "matchpulse-api"
    version: str
    environment: Literal["development", "test", "production"]

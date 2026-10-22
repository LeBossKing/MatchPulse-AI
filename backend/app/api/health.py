from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report API availability; this does not verify Azure or model access."""
    return HealthResponse(
        version=__version__, environment=get_settings().app_env
    )

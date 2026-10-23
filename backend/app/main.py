from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from app import __version__
from app.api.health import router as health_router
from app.api.matches import router as matches_router
from app.api.events import router as events_router
from app.api.errors import fixture_error, http_error, request_validation_error
from app.config import get_settings
from app.services.demo_repository import FixtureLoadError


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="MatchPulse AI API",
        version=__version__,
        description=(
            "Version 1 event/API contract for synthetic football match analysis. "
            "Match reads are implemented; event processing returns 501 until Task 4."
        ),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health_router)
    application.include_router(matches_router)
    application.include_router(events_router)
    application.add_exception_handler(RequestValidationError, request_validation_error)
    application.add_exception_handler(HTTPException, http_error)
    application.add_exception_handler(FixtureLoadError, fixture_error)
    return application


app = create_app()

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from app import __version__
from app.api.health import router as health_router
from app.api.matches import router as matches_router
from app.api.events import router as events_router
from app.api.errors import fixture_error, http_error, request_validation_error, workflow_error
from app.config import get_settings
from app.services.demo_repository import FixtureLoadError
from app.services.workflow import WorkflowError


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="MatchPulse AI API",
        version=__version__,
        description=(
            "Synthetic football analysis with a deterministic three-stage mock workflow, "
            "canonical evidence, audience/language templates, and actual execution traces."
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
    application.add_exception_handler(WorkflowError, workflow_error)
    return application


app = create_app()

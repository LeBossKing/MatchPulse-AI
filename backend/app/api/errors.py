import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.models.error import ApiError, ErrorDetail, ErrorResponse
from app.services.demo_repository import FixtureLoadError
from app.services.workflow import WorkflowError

logger = logging.getLogger(__name__)


async def request_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    details = [
        ErrorDetail(
            field=".".join(str(part) for part in item["loc"]),
            message=item["msg"],
            type=item["type"],
        )
        for item in error.errors()
    ]
    body = ErrorResponse(error=ApiError(
        code="invalid_request", message="The request does not match the API contract.",
        details=details,
    ))
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


async def http_error(request: Request, error: HTTPException) -> JSONResponse:
    if isinstance(error.detail, dict):
        detail = ApiError.model_validate(error.detail)
    else:
        detail = ApiError(
            code="not_found" if error.status_code == 404 else "http_error",
            message=str(error.detail),
        )
    body = ErrorResponse(error=detail)
    return JSONResponse(
        status_code=error.status_code, content=body.model_dump(mode="json"),
        headers=error.headers,
    )


async def fixture_error(request: Request, error: FixtureLoadError) -> JSONResponse:
    logger.error("Demo fixture validation failed: %s", error)
    body = ErrorResponse(error=ApiError(
        code="invalid_fixture", message="The synthetic demo dataset is unavailable or invalid."
    ))
    return JSONResponse(status_code=500, content=body.model_dump(mode="json"))


async def workflow_error(request: Request, error: WorkflowError) -> JSONResponse:
    logger.error("The tactical workflow and mock fallback could not produce a valid result.")
    body = ErrorResponse(error=ApiError(
        code="processing_failed", message="The event analysis is temporarily unavailable."
    ))
    return JSONResponse(status_code=500, content=body.model_dump(mode="json"))

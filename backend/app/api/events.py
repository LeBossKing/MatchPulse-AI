from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from app.models.error import ErrorResponse
from app.models.insight import ProcessEventRequest, ProcessEventResponse
from app.services.demo_repository import load_demo_fixture

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "/process",
    response_model=ProcessEventResponse,
    responses={
        200: {"description": "Reserved success contract. Implemented by the workflow in Task 4."},
        404: {"model": ErrorResponse, "description": "Unknown match or event."},
        422: {"model": ErrorResponse, "description": "Invalid request."},
        500: {"model": ErrorResponse, "description": "Invalid demo fixture."},
        501: {"model": ErrorResponse, "description": "Workflow is not implemented yet."},
    },
)
def process_event(
    request: Annotated[
        ProcessEventRequest,
        Body(openapi_examples={
            "main_event": {
                "summary": "Main synthetic pass, analyst audience, English",
                "value": {
                    "match_id": "match-demo-01", "event_id": "evt-064",
                    "audience": "analyst", "language": "en",
                },
            },
        }),
    ],
) -> ProcessEventResponse:
    """Validate a canonical event selector. Task 3 returns 501, never fake analysis."""
    fixture = load_demo_fixture()
    if request.match_id != fixture.match.match_id:
        raise HTTPException(status_code=404, detail={
            "code": "match_not_found", "message": "The requested demo match does not exist.",
        })
    if not any(event.event_id == request.event_id for event in fixture.events):
        raise HTTPException(status_code=404, detail={
            "code": "event_not_found", "message": "The requested event does not exist in this match.",
        })
    raise HTTPException(status_code=501, detail={
        "code": "processing_not_implemented",
        "message": "The request is valid. The agent workflow will be implemented in Task 4.",
    })

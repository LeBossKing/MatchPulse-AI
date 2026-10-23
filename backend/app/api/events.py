from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException

from app.config import Settings, get_settings
from app.models.error import ErrorResponse
from app.models.insight import ProcessEventRequest, ProcessEventResponse
from app.services.demo_repository import load_demo_fixture
from app.services.providers import ProviderSelection, select_provider
from app.services.workflow import run_workflow

router = APIRouter(prefix="/events", tags=["events"])


def get_provider_selection(settings: Annotated[Settings, Depends(get_settings)]) -> ProviderSelection:
    return select_provider(settings.llm_provider)


@router.post(
    "/process",
    response_model=ProcessEventResponse,
    responses={
        200: {"description": "Processed event, evidence, validation, and actual mock stage traces."},
        404: {"model": ErrorResponse, "description": "Unknown match or event."},
        422: {"model": ErrorResponse, "description": "Invalid request."},
        500: {"model": ErrorResponse, "description": "Invalid fixture or unavailable workflow."},
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
    selection: Annotated[ProviderSelection, Depends(get_provider_selection)],
) -> ProcessEventResponse:
    """Run the three mock stages for a canonical event and presentation preferences."""
    fixture = load_demo_fixture()
    if request.match_id != fixture.match.match_id:
        raise HTTPException(status_code=404, detail={
            "code": "match_not_found", "message": "The requested demo match does not exist.",
        })
    index = next((
        index for index, event in enumerate(fixture.events) if event.event_id == request.event_id
    ), None)
    if index is None:
        raise HTTPException(status_code=404, detail={
            "code": "event_not_found", "message": "The requested event does not exist in this match.",
        })
    return run_workflow(fixture, index, request, selection)

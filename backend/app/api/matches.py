from fastapi import APIRouter

from app.models.error import ErrorResponse
from app.models.match import (
    DemoEventsResponse, DemoMatchResponse, MatchStatistics, TeamStatistics,
)
from app.services.demo_repository import load_demo_fixture

router = APIRouter(prefix="/matches", tags=["matches"])
ERROR_RESPONSES = {500: {"model": ErrorResponse, "description": "Invalid demo fixture."}}


@router.get("/demo", response_model=DemoMatchResponse, responses=ERROR_RESPONSES)
def demo_match() -> DemoMatchResponse:
    """Return metadata and zeroed statistics before replay starts."""
    fixture = load_demo_fixture()
    return DemoMatchResponse(
        review_status=fixture.review_status,
        annotation_note=fixture.annotation_note,
        match=fixture.match,
        statistics=MatchStatistics(teams=[
            TeamStatistics(team_id=fixture.match.home_team.team_id),
            TeamStatistics(team_id=fixture.match.away_team.team_id),
        ]),
    )


@router.get("/demo/events", response_model=DemoEventsResponse, responses=ERROR_RESPONSES)
def demo_events() -> DemoEventsResponse:
    """Return canonical events; missing tactical annotations remain null."""
    fixture = load_demo_fixture()
    return DemoEventsResponse(
        match_id=fixture.match.match_id, review_status=fixture.review_status,
        main_event_id=fixture.main_event_id, events=fixture.events,
    )

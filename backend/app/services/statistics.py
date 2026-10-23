"""Pure calculations over a selected event and the canonical sequence prefix."""

from math import hypot

from app.models.event import MatchEvent
from app.models.insight import EventStatistics
from app.models.match import DemoFixture, MatchStatistics, TeamStatistics


def event_statistics(event: MatchEvent) -> EventStatistics:
    if event.event_type != "pass":
        return EventStatistics()
    assert event.end is not None  # Guaranteed by the event contract.
    dx = event.end.x - event.start.x
    dy = event.end.y - event.start.y
    direction = 1 if event.attacking_direction == "left_to_right" else -1
    return EventStatistics(
        pass_length=round(hypot(dx, dy), 2),
        forward_progression=round(direction * dx, 2),
    )


def prefix_statistics(fixture: DemoFixture, event_index: int) -> MatchStatistics:
    if not 0 <= event_index < len(fixture.events):
        raise IndexError("The selected event is outside the canonical sequence.")
    prefix = fixture.events[:event_index + 1]
    teams = []
    for team_id in (fixture.match.home_team.team_id, fixture.match.away_team.team_id):
        events = [event for event in prefix if event.team_id == team_id]
        passes = [event for event in events if event.event_type == "pass"]
        completed = sum(event.successful for event in passes)
        teams.append(TeamStatistics(
            team_id=team_id,
            passes_attempted=len(passes),
            passes_completed=completed,
            pass_accuracy_pct=round(100 * completed / len(passes), 2) if passes else None,
            interceptions=sum(event.event_type == "interception" for event in events),
            recoveries=sum(event.event_type == "recovery" for event in events),
        ))
    return MatchStatistics(
        event_count=len(prefix), through_event_id=prefix[-1].event_id, teams=teams,
    )

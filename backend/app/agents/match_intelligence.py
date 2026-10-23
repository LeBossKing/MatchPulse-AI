from app.agents.contracts import IntelligenceResult
from app.models.insight import EvidenceItem, Overlay
from app.models.match import DemoFixture
from app.services.statistics import event_statistics, prefix_statistics


def analyze_event(fixture: DemoFixture, event_index: int) -> IntelligenceResult:
    # Never hand the process-cached fixture's mutable objects to later stages.
    event = fixture.events[event_index].model_copy(deep=True)
    statistics = event_statistics(event)
    evidence = []
    for field in (
        "event_type", "team_id", "player_id", "target_player_id",
        "attacking_direction", "successful", "pressure", "lines_broken",
    ):
        value = getattr(event, field)
        if value is not None:
            evidence.append(EvidenceItem(
                evidence_id="ev-" + field.replace("_", "-"),
                source="event", field=field, value=value,
            ))
    for name, point in (("start", event.start), ("end", event.end)):
        if point is not None:
            for axis in ("x", "y"):
                evidence.append(EvidenceItem(
                    evidence_id=f"ev-{name}-{axis}", source="event",
                    field=f"{name}.{axis}", value=getattr(point, axis),
                ))
    for field in ("pass_length", "forward_progression"):
        value = getattr(statistics, field)
        if value is not None:
            evidence.append(EvidenceItem(
                evidence_id="ev-" + field.replace("_", "-"),
                source="statistics", field=field, value=value,
            ))
    return IntelligenceResult(
        event=event, statistics=statistics,
        match_statistics=prefix_statistics(fixture, event_index), evidence=evidence,
        overlay=Overlay(
            kind="pass" if event.event_type == "pass" else "point",
            start=event.start.model_copy(), end=event.end.model_copy() if event.end else None,
        ),
    )

"""Explicit demo heuristics; these are not learned tactical ratings."""

from app.agents.contracts import IntelligenceResult, TacticalCandidate


def interpretation_for(facts: IntelligenceResult) -> str:
    event = facts.event
    if event.event_type != "pass":
        return "regain"
    if not event.successful:
        return "attempt_failed"
    return "advance" if facts.statistics.forward_progression > 0 else "retain"


def importance_for(facts: IntelligenceResult) -> str:
    event = facts.event
    if event.event_type != "pass":
        return "medium"
    if not event.successful:
        return "low"
    progression = facts.statistics.forward_progression
    if progression >= 20 and (event.lines_broken or 0) >= 1:
        return "high"
    return "medium" if progression >= 15 else "low"


def mock_candidate(facts: IntelligenceResult) -> TacticalCandidate:
    return TacticalCandidate(
        event_id=facts.event.event_id,
        claims=[item.model_copy(deep=True) for item in facts.evidence],
        interpretation=interpretation_for(facts), importance=importance_for(facts),
    )

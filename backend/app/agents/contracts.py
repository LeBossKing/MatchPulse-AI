"""Internal stage contracts. Providers supply claims, never unchecked narrative text."""

from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import Field

from app.models.common import ContractModel, Identifier
from app.models.event import MatchEvent
from app.models.insight import EvidenceItem, EventStatistics, Insight, Overlay, ValidationResult
from app.models.match import MatchStatistics


@dataclass(frozen=True)
class IntelligenceResult:
    event: MatchEvent
    statistics: EventStatistics
    match_statistics: MatchStatistics
    evidence: list[EvidenceItem]
    overlay: Overlay


class TacticalCandidate(ContractModel):
    event_id: Identifier
    claims: Annotated[list[EvidenceItem], Field(min_length=1, max_length=24)]
    interpretation: Literal["advance", "retain", "attempt_failed", "regain"]
    importance: Literal["low", "medium", "high"]


@dataclass(frozen=True)
class TrustResult:
    insight: Insight | None
    validation: ValidationResult

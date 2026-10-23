from typing import Annotated, Literal, Self

from pydantic import Field, JsonValue, StrictBool, StrictFloat, StrictInt, StrictStr, model_validator

from app.models.common import Audience, ContractModel, Identifier, Language, ReviewStatus, SchemaVersion
from app.models.event import MatchEvent, Point
from app.models.match import MatchStatistics

AgentName = Literal["match_intelligence", "tactical_explainer", "trust_personalization"]
AGENT_ORDER = ("match_intelligence", "tactical_explainer", "trust_personalization")


class ProcessEventRequest(ContractModel):
    match_id: Identifier
    event_id: Identifier
    audience: Audience = "analyst"
    language: Language = "en"


class EventStatistics(ContractModel):
    units: Literal["normalized_pitch_units"] = "normalized_pitch_units"
    pass_length: Annotated[float, Field(ge=0, le=142, allow_inf_nan=False)] | None = None
    forward_progression: Annotated[
        float, Field(ge=-100, le=100, allow_inf_nan=False)
    ] | None = None


class EvidenceItem(ContractModel):
    evidence_id: Identifier
    source: Literal["event", "statistics"]
    field: Annotated[str, Field(pattern=r"^[a-z_]+(?:\.[a-z_]+)*$")]
    value: StrictBool | StrictInt | StrictFloat | StrictStr


class Insight(ContractModel):
    title: Annotated[str, Field(min_length=1, max_length=120)]
    explanation: Annotated[str, Field(min_length=1, max_length=1200)]
    interpretation: Annotated[str, Field(min_length=1, max_length=600)] | None = None
    importance: Literal["low", "medium", "high"]
    evidence_ids: Annotated[list[Identifier], Field(min_length=1)]


class ValidationResult(ContractModel):
    status: Literal["validated", "limited", "rejected"]
    unsupported_claims: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_validation(self) -> Self:
        if self.status == "validated" and self.unsupported_claims:
            raise ValueError("A validated insight cannot retain unsupported claims.")
        return self


class Overlay(ContractModel):
    kind: Literal["pass", "point"]
    start: Point
    end: Point | None = None


class AgentTraceStep(ContractModel):
    agent: AgentName
    status: Literal["completed", "skipped", "failed"]
    duration_ms: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    summary: Annotated[str, Field(min_length=1, max_length=500)]
    output: dict[str, JsonValue] = Field(default_factory=dict)


class ProcessEventResponse(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    status: Literal["processed"] = "processed"
    result_source: Literal["runtime", "example"] = "runtime"
    data_source: Literal["synthetic"] = "synthetic"
    review_status: ReviewStatus
    match_id: Identifier
    event_id: Identifier
    event: MatchEvent
    audience: Audience
    language: Language
    provider: Literal["mock", "azure", "fallback"]
    statistics: EventStatistics
    match_statistics: MatchStatistics
    insight: Insight | None
    evidence: list[EvidenceItem]
    validation: ValidationResult
    overlay: Overlay
    agent_trace: Annotated[list[AgentTraceStep], Field(min_length=3, max_length=3)]
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_response_consistency(self) -> Self:
        if self.event_id != self.event.event_id or self.match_id != self.event.match_id:
            raise ValueError("Envelope identifiers must match the selected event.")
        if self.match_statistics.through_event_id != self.event_id:
            raise ValueError("Match statistics must end at the selected event.")
        if tuple(step.agent for step in self.agent_trace) != AGENT_ORDER:
            raise ValueError("The trace must contain the three distinct agents in workflow order.")
        if (self.insight is None) != (self.validation.status == "rejected"):
            raise ValueError("A rejected insight must be null; other results require an insight.")
        if self.provider == "fallback" and not self.warnings:
            raise ValueError("A fallback must carry a visible warning.")
        expected_kind = "pass" if self.event.event_type == "pass" else "point"
        if (
            self.overlay.kind != expected_kind
            or self.overlay.start != self.event.start
            or self.overlay.end != self.event.end
        ):
            raise ValueError("The overlay must match the selected event coordinates and type.")
        has_pass_metrics = (
            self.statistics.pass_length is not None
            and self.statistics.forward_progression is not None
        )
        if self.event.event_type == "pass":
            if not has_pass_metrics:
                raise ValueError("A pass response requires length and progression.")
        elif self.statistics.pass_length is not None or self.statistics.forward_progression is not None:
            raise ValueError("Point events cannot carry pass metrics.")
        evidence_ids = [item.evidence_id for item in self.evidence]
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("Evidence identifiers must be unique.")
        if self.insight and not set(self.insight.evidence_ids).issubset(evidence_ids):
            raise ValueError("An insight cannot reference missing evidence.")
        sources = {
            "event": self.event.model_dump(mode="json"),
            "statistics": self.statistics.model_dump(mode="json"),
        }
        for item in self.evidence:
            actual = sources[item.source]
            for key in item.field.split("."):
                if not isinstance(actual, dict) or key not in actual:
                    raise ValueError("Evidence must reference an available source field.")
                actual = actual[key]
            if actual is None or isinstance(actual, (dict, list)):
                raise ValueError("Evidence must reference a known primitive value.")
            if isinstance(actual, bool) != isinstance(item.value, bool) or actual != item.value:
                raise ValueError("Evidence values must match their source fields.")
        return self

"""Provider boundary for the mock milestone. No model or Azure SDK is called."""

from dataclasses import dataclass
from typing import Literal, Protocol

from app.agents.contracts import IntelligenceResult, TacticalCandidate
from app.agents.tactical_explainer import mock_candidate


class ProviderError(Exception):
    """An expected upstream failure. Exception messages never go to the client."""


class TacticalProvider(Protocol):
    name: str

    def generate(self, facts: IntelligenceResult) -> TacticalCandidate: ...


class MockTacticalProvider:
    name = "mock"

    def generate(self, facts: IntelligenceResult) -> TacticalCandidate:
        return mock_candidate(facts)


@dataclass(frozen=True)
class ProviderSelection:
    provider: TacticalProvider
    requested: Literal["mock", "azure"]
    fallback_reason: Literal["azure_not_implemented"] | None = None


def select_provider(requested: Literal["mock", "azure"]) -> ProviderSelection:
    return ProviderSelection(
        provider=MockTacticalProvider(), requested=requested,
        fallback_reason="azure_not_implemented" if requested == "azure" else None,
    )

"""Choose mock or configured Azure inference without making a request at selection time."""

from dataclasses import dataclass
from typing import Literal, Protocol

from app.agents.contracts import IntelligenceResult, TacticalCandidate
from app.agents.tactical_explainer import mock_candidate
from app.config import Settings, get_settings
from app.services.azure_config import AzureConfigurationError, azure_configuration
from app.services.azure_openai import AzureTacticalProvider
from app.services.provider_errors import ProviderError  # Re-export for existing callers.


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
    fallback_reason: Literal["azure_configuration"] | None = None


def select_provider(requested: Literal["mock", "azure"], settings: Settings | None = None) -> ProviderSelection:
    if requested == "mock":
        return ProviderSelection(provider=MockTacticalProvider(), requested=requested)
    try:
        config = azure_configuration(settings or get_settings())
    except AzureConfigurationError:
        return ProviderSelection(
            provider=MockTacticalProvider(), requested=requested,
            fallback_reason="azure_configuration",
        )
    return ProviderSelection(provider=AzureTacticalProvider(config), requested=requested)

"""Member 2 rule adaptations for the current synthetic, structured-candidate MVP.

These are not executions of the original StatsBomb/text-input specifications.
"""

import json

import pytest

from app.agents.match_intelligence import analyze_event
from app.agents.tactical_explainer import mock_candidate
from app.agents.trust_personalization import validate_and_personalize
from app.api.events import get_provider_selection
from app.models.insight import EvidenceItem, ProcessEventResponse
from app.models.match import DemoFixture
import app.services.demo_repository as repository
from app.services.providers import ProviderError, ProviderSelection


SELECTOR = {"match_id": "match-demo-01", "event_id": "evt-064"}
PREFERENCES = [(audience, language) for audience in ("analyst", "fan") for language in ("en", "fr")]


@pytest.mark.parametrize("field,value", [
    ("pressure", "high"), ("pressure", "low"), ("lines_broken", 2),
])
@pytest.mark.parametrize("audience,language", PREFERENCES)
def test_unknown_annotations_cannot_be_promoted_to_known_claims(field, value, audience, language):
    fixture = repository.load_demo_fixture()
    facts = analyze_event(fixture, 6)  # evt-067 has neither tactical annotation.
    candidate = mock_candidate(facts)
    candidate.claims.append(EvidenceItem(
        evidence_id="ev-" + field.replace("_", "-"),
        source="event", field=field, value=value,
    ))
    result = validate_and_personalize(fixture, facts, candidate, audience, language)
    assert result.validation.status == "rejected" and result.insight is None
    assert result.validation.unsupported_claims
    assert facts.event.pressure is None and facts.event.lines_broken is None


@pytest.mark.parametrize("field", ["goal_scored", "guaranteed_goal"])
def test_unsupported_scoring_claims_are_rejected(field):
    fixture = repository.load_demo_fixture()
    facts = analyze_event(fixture, 3)
    candidate = mock_candidate(facts)
    candidate.claims.append(EvidenceItem(
        evidence_id="ev-" + field.replace("_", "-"),
        source="event", field=field, value=True,
    ))
    result = validate_and_personalize(fixture, facts, candidate, "analyst", "en")
    assert result.validation.status == "rejected" and result.insight is None
    assert any(field in error for error in result.validation.unsupported_claims)


@pytest.mark.parametrize("audience,language", PREFERENCES)
def test_published_metrics_and_narrative_keep_normalized_units(client, audience, language):
    response = client.post("/events/process", json=SELECTOR | {
        "audience": audience, "language": language,
    })
    assert response.status_code == 200
    result = ProcessEventResponse.model_validate(response.json())
    assert result.statistics.units == "normalized_pitch_units"
    assert result.statistics.pass_length == 44.28
    assert result.statistics.forward_progression == 40
    text = result.insight.explanation
    assert ("normalisées" if language == "fr" else "normalized") in text
    assert all(unit not in text.lower() for unit in ("metres", "meters", "mètres"))


def test_unchecked_provider_prose_cannot_be_added_to_an_otherwise_valid_candidate(client):
    injected = "Jorginho scored; this 19.77 metres pass guaranteed a goal."

    class ProseProvider:
        name = "mock"

        def generate(self, facts):
            return mock_candidate(facts).model_dump(mode="json") | {"free_text": injected}

    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(ProseProvider(), "mock")
    response = client.post("/events/process", json=SELECTOR)
    assert response.status_code == 200
    result = ProcessEventResponse.model_validate(response.json())
    assert result.provider == "fallback"
    assert result.agent_trace[1].output["fallback_reason"] == "provider_error"
    assert injected not in response.text and "Jorginho" not in response.text
    assert result.insight is not None


@pytest.mark.parametrize("mutation", ["missing_start", "missing_end", "invalid_start", "invalid_end"])
def test_invalid_fixture_stops_before_tactical_generation(client, fixture_data, monkeypatch, tmp_path, mutation):
    event = fixture_data["events"][3]
    if mutation == "missing_start":
        event.pop("start")
    elif mutation == "missing_end":
        event.pop("end")
    elif mutation == "invalid_start":
        event["start"]["x"] = 101  # Current contract is normalized 0-100.
    else:
        event["end"]["y"] = -1
    path = tmp_path / "invalid-fixture.json"
    path.write_text(json.dumps(fixture_data), encoding="utf-8")
    monkeypatch.setattr(repository, "FIXTURE_PATH", path)
    repository.load_demo_fixture.cache_clear()
    calls = []

    class TrackingProvider:
        name = "mock"

        def generate(self, facts):
            calls.append(facts.event.event_id)
            return mock_candidate(facts)

    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(TrackingProvider(), "mock")
    response = client.post("/events/process", json=SELECTOR)
    # Corrupt server fixtures are server errors, not client-selector errors.
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "invalid_fixture"
    assert "insight" not in response.json() and calls == []


def test_a_failed_attempt_cannot_be_rewritten_as_a_completed_pass(fixture_data):
    fixture_data["events"][3]["successful"] = False
    fixture_data["events"][3]["lines_broken"] = None
    fixture = DemoFixture.model_validate(fixture_data)
    facts = analyze_event(fixture, 3)
    candidate = mock_candidate(facts)
    next(item for item in candidate.claims if item.field == "successful").value = True
    result = validate_and_personalize(fixture, facts, candidate, "fan", "en")
    assert result.insight is None and result.validation.status == "rejected"
    assert facts.event.successful is False
    assert any("successful" in error for error in result.validation.unsupported_claims)


def test_azure_timeout_is_visible_as_fallback_at_the_api_boundary(client):
    class TimeoutProvider:
        name = "azure"

        def generate(self, facts):
            raise ProviderError("private-timeout-detail", reason="azure_timeout")

    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(TimeoutProvider(), "azure")
    response = client.post("/events/process", json=SELECTOR | {"audience": "fan", "language": "fr"})
    assert response.status_code == 200
    result = ProcessEventResponse.model_validate(response.json())
    assert result.provider == "fallback" and result.insight is not None
    trace = result.agent_trace[1].output
    assert trace["requested_provider"] == "azure" and trace["actual_provider"] == "mock"
    assert trace["fallback_reason"] == "azure_timeout"
    assert trace["attempts"] == [
        {"provider": "azure", "status": "failed"},
        {"provider": "mock", "status": "completed"},
    ]
    assert result.warnings and result.language == "fr"
    assert "private-timeout-detail" not in response.text

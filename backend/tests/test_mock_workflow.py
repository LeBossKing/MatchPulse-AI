from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path

import pytest

from app.agents.match_intelligence import analyze_event
from app.agents.tactical_explainer import mock_candidate
from app.agents.trust_personalization import validate_and_personalize
from app.api.events import get_provider_selection
from app.config import get_settings
from app.models.insight import AGENT_ORDER, EvidenceItem, ProcessEventRequest, ProcessEventResponse
from app.models.match import DemoFixture
from app.services.demo_repository import load_demo_fixture
from app.services.providers import MockTacticalProvider, ProviderError, ProviderSelection, select_provider
from app.services.workflow import run_workflow

SELECTOR = {"match_id": "match-demo-01", "event_id": "evt-064"}
EXAMPLES = Path(__file__).resolve().parents[1] / "data" / "examples"


def process(client, event_id="evt-064", **preferences):
    response = client.post("/events/process", json=SELECTOR | {"event_id": event_id} | preferences)
    assert response.status_code == 200, response.text
    return ProcessEventResponse.model_validate(response.json())


def test_main_event_matches_the_agreed_calculations_and_counts(client):
    result = process(client)
    assert result.statistics.pass_length == 44.28
    assert result.statistics.forward_progression == 40
    atlas, harbor = result.match_statistics.teams
    assert (atlas.passes_attempted, atlas.passes_completed, atlas.pass_accuracy_pct) == (4, 4, 100)
    assert (harbor.passes_attempted, harbor.pass_accuracy_pct) == (0, None)
    assert result.match_statistics.event_count == 4
    assert result.validation.status == "validated"
    assert result.insight.importance == "high"
    assert result.event.pressure == "high" and result.event.lines_broken == 1
    assert result.review_status == "pending_review"
    assert tuple(step.agent for step in result.agent_trace) == AGENT_ORDER
    assert all(step.status == "completed" and step.duration_ms >= 0 for step in result.agent_trace)
    assert result.agent_trace[0].output["statistics"] == result.statistics.model_dump(mode="json")
    assert result.agent_trace[2].output["insight"] == result.insight.model_dump(mode="json")
    assert any("no model" in warning for warning in result.warnings)


@pytest.mark.parametrize("event_id", [f"evt-{index:03d}" for index in range(61, 69)])
@pytest.mark.parametrize("audience,language", [("analyst", "en"), ("fan", "en"), ("analyst", "fr"), ("fan", "fr")])
def test_every_fixture_event_runs_in_both_modes_and_languages(client, event_id, audience, language):
    result = process(client, event_id, audience=audience, language=language)
    fixture = load_demo_fixture()
    index = next(i for i, event in enumerate(fixture.events) if event.event_id == event_id)
    assert result.event == fixture.events[index]
    assert result.result_source == "runtime" and result.insight is not None
    assert result.match_statistics.event_count == index + 1
    assert (result.audience, result.language) == (audience, language)
    assert len(result.evidence) == len(result.insight.evidence_ids)


def test_variants_preserve_facts_but_change_presentation(client):
    results = [process(client, audience=audience, language=language)
               for audience in ("analyst", "fan") for language in ("en", "fr")]
    for result in results[1:]:
        assert result.event == results[0].event
        assert result.statistics == results[0].statistics
        assert result.match_statistics == results[0].match_statistics
        assert result.evidence == results[0].evidence
    assert len({result.insight.explanation for result in results}) == 4
    assert "44,28" in results[1].insight.explanation
    assert "forte" in results[1].insight.explanation


def test_replay_and_rewind_do_not_double_count_or_mutate_the_fixture(client):
    initial = client.get("/matches/demo").json()
    fixture_before = load_demo_fixture().model_dump()
    final = process(client, "evt-068")
    assert final.match_statistics.teams[0].pass_accuracy_pct == 80
    assert final.match_statistics.teams[1].interceptions == 1
    assert final.match_statistics.teams[0].recoveries == 1
    first = process(client, "evt-061")
    assert first.match_statistics.event_count == 1
    assert first.match_statistics.teams[0].passes_attempted == 1
    assert process(client, "evt-068").match_statistics == final.match_statistics
    assert client.get("/matches/demo").json() == initial
    assert load_demo_fixture().model_dump() == fixture_before


def test_backward_failed_and_missing_context_are_not_misrepresented(client):
    backward = process(client, "evt-063", audience="fan")
    assert backward.statistics.forward_progression == -7
    assert "backward" in backward.insight.explanation
    assert backward.insight.importance == "low"
    failed = process(client, "evt-065")
    assert failed.event.successful is False
    assert "not completed" in failed.insight.explanation
    assert failed.insight.importance == "low"
    assert "not a completed gain" in failed.insight.explanation
    unknown = process(client, "evt-067")
    assert unknown.statistics.forward_progression == 16
    assert unknown.validation.status == "limited"
    assert unknown.event.pressure is None and unknown.event.lines_broken is None
    assert not {"pressure", "lines_broken"}.intersection(item.field for item in unknown.evidence)


@pytest.mark.parametrize("event_id", ["evt-066", "evt-068"])
def test_regains_have_point_overlays_and_no_invented_pass_metrics(client, event_id):
    result = process(client, event_id)
    assert result.overlay.kind == "point" and result.overlay.end is None
    assert result.statistics.pass_length is None and result.statistics.forward_progression is None
    assert all(item.source != "statistics" for item in result.evidence)


def test_missing_receiver_and_zero_progression_are_rendered_without_invention(fixture_data):
    fixture_data["events"][4]["target_player_id"] = None
    fixture = DemoFixture.model_validate(fixture_data)
    failed = run_workflow(fixture, 4, ProcessEventRequest(**SELECTOR | {"event_id": "evt-065"}), select_provider("mock"))
    assert "unspecified receiver" in failed.insight.explanation and "None" not in failed.insight.explanation
    fixture_data["events"][0]["end"]["x"] = fixture_data["events"][0]["start"]["x"]
    fixture = DemoFixture.model_validate(fixture_data)
    lateral = run_workflow(fixture, 0, ProcessEventRequest(**SELECTOR | {"event_id": "evt-061", "audience": "fan"}), select_provider("mock"))
    assert lateral.statistics.forward_progression == 0
    assert "no forward progression" in lateral.insight.explanation
    assert lateral.validation.status == "validated"  # Explicit zero lines is known, not missing.


@pytest.mark.parametrize("corruption", [
    "wrong_value", "bool_as_number", "unknown_claim", "missing_claim", "duplicate_claim",
    "wrong_event", "wrong_interpretation", "wrong_importance", "wrong_field", "wrong_source",
])
def test_trust_rejects_conflicting_or_unsupported_structured_claims(corruption):
    fixture = load_demo_fixture()
    facts = analyze_event(fixture, 3)
    candidate = mock_candidate(facts)
    if corruption == "wrong_value":
        next(item for item in candidate.claims if item.field == "lines_broken").value = 2
    elif corruption == "bool_as_number":
        next(item for item in candidate.claims if item.field == "lines_broken").value = True
    elif corruption == "unknown_claim":
        candidate.claims.append(EvidenceItem(evidence_id="ev-shot", source="event", field="shot_created", value=True))
    elif corruption == "missing_claim":
        candidate.claims.pop()
    elif corruption == "duplicate_claim":
        candidate.claims.append(candidate.claims[0].model_copy())
    elif corruption == "wrong_event":
        candidate.event_id = "evt-065"
    elif corruption == "wrong_interpretation":
        candidate.interpretation = "regain"
    elif corruption == "wrong_importance":
        candidate.importance = "low"
    elif corruption == "wrong_field":
        candidate.claims[0].field = "pressure"
    elif corruption == "wrong_source":
        candidate.claims[0].source = "statistics"
    result = validate_and_personalize(fixture, facts, candidate, "analyst", "en")
    assert result.insight is None and result.validation.status == "rejected"
    assert result.validation.unsupported_claims


def test_rejected_candidate_is_visible_in_api_response(client):
    class ConflictingProvider:
        name = "mock"

        def generate(self, facts):
            result = mock_candidate(facts)
            next(item for item in result.claims if item.field == "lines_broken").value = 3
            return result

    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(ConflictingProvider(), "mock")
    result = process(client)
    assert result.insight is None and result.validation.status == "rejected"
    assert result.agent_trace[-1].status == "completed"  # The check executed successfully.
    assert result.validation.unsupported_claims
    assert any("rejected" in warning for warning in result.warnings)


@pytest.mark.parametrize("failure", ["exception", "invalid_structure"])
def test_provider_failure_uses_a_visible_mock_fallback_without_leaking_details(client, failure):
    class BrokenProvider:
        name = "mock"

        def generate(self, facts):
            if failure == "exception":
                raise ProviderError("do-not-leak-secret")
            return {"free_text": "unsupported prose", "secret": "do-not-leak-secret"}

    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(BrokenProvider(), "mock")
    result = process(client)
    assert result.provider == "fallback" and result.insight is not None
    trace = result.agent_trace[1]
    assert trace.output["fallback_reason"] == "provider_error"
    assert [attempt["status"] for attempt in trace.output["attempts"]] == ["failed", "completed"]
    assert "do-not-leak-secret" not in result.model_dump_json()


def test_missing_azure_configuration_is_honestly_reported_as_fallback(client, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "azure")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "do-not-leak-azure-secret")
    get_settings.cache_clear()
    result = process(client)
    assert result.provider == "fallback"
    assert any("without sending an Azure request" in warning for warning in result.warnings)
    trace = result.agent_trace[1].output
    assert trace["requested_provider"] == "azure" and trace["actual_provider"] == "mock"
    assert trace["fallback_reason"] == "azure_configuration"
    assert trace["attempts"] == [{"provider": "mock", "status": "completed"}]
    assert "do-not-leak-azure-secret" not in result.model_dump_json()


def test_unrecoverable_provider_failure_returns_the_typed_server_error(client, monkeypatch):
    def fail(self, facts):
        raise ProviderError("private-failure-detail")

    monkeypatch.setattr(MockTacticalProvider, "generate", fail)
    response = client.post("/events/process", json=SELECTOR)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "processing_failed"
    assert "private-failure-detail" not in response.text


def test_provider_cannot_mutate_the_trusted_snapshot(client):
    class MutatingProvider:
        name = "mock"

        def generate(self, facts):
            facts.event.lines_broken = 12
            facts.statistics.pass_length = 1
            return mock_candidate(facts)

    before = load_demo_fixture().model_dump()
    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(MutatingProvider(), "mock")
    result = process(client)
    assert result.statistics.pass_length == 44.28 and result.event.lines_broken == 1
    assert load_demo_fixture().model_dump() == before


def test_parallel_selections_are_independent():
    fixture = load_demo_fixture()
    before = deepcopy(fixture.model_dump())

    def run(index):
        request = ProcessEventRequest(match_id=fixture.match.match_id, event_id=fixture.events[index].event_id)
        return run_workflow(fixture, index, request, select_provider("mock"))

    indices = [7, 0, 3, 6, 3, 7]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(run, indices))
    assert [result.match_statistics.event_count for result in results] == [8, 1, 4, 7, 4, 8]
    assert fixture.model_dump() == before


@pytest.mark.parametrize("filename", [
    "main-analyst-en", "unsuccessful-pass", "interception", "missing-annotations", "recovery",
])
def test_runtime_calculations_match_the_task3_example_facts(client, filename):
    example = json.loads((EXAMPLES / f"{filename}.json").read_text())
    result = process(client, example["event_id"])
    assert result.statistics.model_dump(mode="json") == example["statistics"]
    assert result.match_statistics.model_dump(mode="json") == example["match_statistics"]

from app.models.error import ErrorResponse
from app.models.insight import ProcessEventResponse
from app.models.match import DemoEventsResponse, DemoMatchResponse
import app.services.demo_repository as repository


SELECTOR = {"match_id": "match-demo-01", "event_id": "evt-064"}


def test_match_and_event_reads_return_validated_synthetic_data(client):
    match = DemoMatchResponse.model_validate(client.get("/matches/demo").json())
    events = DemoEventsResponse.model_validate(client.get("/matches/demo/events").json())
    assert match.data_source == events.data_source == "synthetic"
    assert match.review_status == events.review_status == "pending_review"
    assert events.main_event_id == "evt-064" and len(events.events) == 8
    assert match.statistics.event_count == 0
    assert all(team.pass_accuracy_pct is None for team in match.statistics.teams)
    assert events.events[6].pressure is None and events.events[6].lines_broken is None


def test_valid_selector_executes_the_mock_workflow(client):
    response = client.post("/events/process", json=SELECTOR)
    assert response.status_code == 200
    body = ProcessEventResponse.model_validate(response.json())
    assert body.result_source == "runtime" and body.provider == "mock"
    assert body.insight is not None
    assert len(body.agent_trace) == 3


def test_unknown_match_and_event_have_distinct_errors(client):
    for changed, code in [
        ({"match_id": "missing"}, "match_not_found"),
        ({"event_id": "missing"}, "event_not_found"),
    ]:
        response = client.post("/events/process", json=SELECTOR | changed)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == code


def test_request_validation_has_field_errors_without_echoing_inputs(client):
    response = client.post(
        "/events/process", json=SELECTOR | {"audience": "unsupported", "api_key": "do-not-echo"}
    )
    assert response.status_code == 422
    body = ErrorResponse.model_validate(response.json())
    assert body.error.code == "invalid_request"
    assert {item.field for item in body.error.details} == {"body.audience", "body.api_key"}
    assert "do-not-echo" not in response.text


def test_selectors_do_not_accept_client_authored_event_facts(client):
    response = client.post("/events/process", json=SELECTOR | {"event": {"successful": True}})
    assert response.status_code == 422


def test_personalization_does_not_mutate_initial_match_state(client):
    before = client.get("/matches/demo").json()
    for audience in ["fan", "analyst"]:
        for language in ["en", "fr"]:
            response = client.post(
                "/events/process", json=SELECTOR | {"audience": audience, "language": language}
            )
            assert response.status_code == 200
    assert client.get("/matches/demo").json() == before


def test_invalid_fixture_produces_a_structured_server_error(client, monkeypatch, tmp_path):
    bad_fixture = tmp_path / "invalid.json"
    bad_fixture.write_text('{"events": []}')
    monkeypatch.setattr(repository, "FIXTURE_PATH", bad_fixture)
    repository.load_demo_fixture.cache_clear()
    response = client.get("/matches/demo/events")
    assert response.status_code == 500
    assert ErrorResponse.model_validate(response.json()).error.code == "invalid_fixture"


def test_openapi_declares_success_and_current_error_contracts(client):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/events/process"]["post"]
    assert {"200", "404", "422", "500"}.issubset(operation["responses"])
    assert "501" not in operation["responses"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith("ProcessEventResponse")
    assert client.get("/health").json()["status"] == "ok"

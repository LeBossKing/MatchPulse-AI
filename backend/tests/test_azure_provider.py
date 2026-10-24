import json

import httpx
import pytest

from app.agents.match_intelligence import analyze_event
from app.agents.tactical_explainer import mock_candidate
from app.api.events import get_provider_selection
from app.config import Settings
from app.models.insight import ProcessEventResponse
from app.services.azure_config import AzureConfigurationError, azure_configuration
from app.services.azure_openai import AzureTacticalProvider, candidate_schema
from app.services.demo_repository import load_demo_fixture
from app.services.provider_errors import ProviderError
from app.services.providers import ProviderSelection, select_provider
from scripts.check_azure import check_azure, main


def settings(**changes):
    return Settings(_env_file=None, **({
        "llm_provider": "azure", "azure_openai_endpoint": "https://matchpulse-tests.openai.azure.com/",
        "azure_openai_deployment": "matchpulse-tactical", "azure_openai_api_key": "unit-test-secret",
        "azure_openai_timeout_seconds": 8, "azure_openai_max_output_tokens": 2048,
    } | changes))


def facts():
    return analyze_event(load_demo_fixture(), 3)


def response_body(candidate=None):
    candidate = candidate or mock_candidate(facts())
    return {
        "status": "completed", "extra_future_field": "ignored",
        "output": [{"type": "reasoning", "summary": []}, {
            "type": "message", "role": "assistant", "status": "completed",
            "content": [{"type": "output_text", "text": candidate.model_dump_json()}],
        }],
    }


@pytest.mark.parametrize("endpoint", [
    "https://matchpulse-tests.openai.azure.com", "https://matchpulse-tests.openai.azure.com/openai/v1/",
    "https://matchpulse-tests.services.ai.azure.com/", "https://matchpulse-tests.services.ai.azure.com/openai/v1",
])
def test_supported_resource_endpoints_are_normalized(endpoint):
    config = azure_configuration(settings(azure_openai_endpoint=endpoint))
    assert config.base_url.endswith("/openai/v1/")
    assert config.base_url.count("/openai/v1/") == 1
    assert "unit-test-secret" not in repr(config)


@pytest.mark.parametrize("endpoint", [
    "http://matchpulse-tests.openai.azure.com", "https://api.openai.com",
    "https://matchpulse-tests.openai.azure.com.evil.invalid", "https://localhost",
    "https://user:private-password@matchpulse-tests.openai.azure.com",
    "https://matchpulse-tests.openai.azure.com/?api-key=private-password",
    "https://matchpulse-tests.openai.azure.com/#private-password",
    "https://matchpulse-tests.openai.azure.com:8443",
    "https://matchpulse-tests.openai.azure.com/api/projects/demo",
    "https://matchpulse-tests.openai.azure.com:bad-port",
])
def test_invalid_endpoints_do_not_receive_credentials_or_echo_values(endpoint):
    with pytest.raises(AzureConfigurationError) as caught:
        azure_configuration(settings(azure_openai_endpoint=endpoint))
    assert "private-password" not in str(caught.value) + str(caught.value.issues)


def test_mock_selection_does_not_require_or_validate_azure_settings():
    selection = select_provider("mock", settings(azure_openai_endpoint="not-a-url"))
    assert selection.provider.name == "mock" and selection.fallback_reason is None


def test_incomplete_configuration_selects_visible_fallback_without_a_network_call():
    selection = select_provider("azure", settings(azure_openai_api_key=""))
    assert selection.provider.name == "mock" and selection.fallback_reason == "azure_configuration"


def test_live_request_uses_v1_deployment_schema_limits_and_exactly_one_call():
    requests = []

    def handle(request):
        requests.append(request)
        assert str(request.url) == "https://matchpulse-tests.openai.azure.com/openai/v1/responses"
        assert request.headers["api-key"] == "unit-test-secret"
        payload = json.loads(request.content)
        assert payload["model"] == "matchpulse-tactical"
        assert payload["store"] is False and payload["max_output_tokens"] == 2048
        assert payload["text"]["format"]["strict"] is True
        assert payload["text"]["format"]["type"] == "json_schema"
        assert "unit-test-secret" not in request.content.decode()
        assert json.loads(payload["input"])["evidence"] == [item.model_dump(mode="json") for item in facts().evidence]
        assert request.extensions["timeout"]["read"] == 8
        assert request.extensions["timeout"]["connect"] == 5
        return httpx.Response(200, json=response_body())

    provider = AzureTacticalProvider(azure_configuration(settings()), transport=httpx.MockTransport(handle))
    result = provider.generate(facts())
    assert result == mock_candidate(facts())
    assert len(requests) == 1


def test_azure_schema_uses_supported_keywords_and_closed_required_objects():
    schema = candidate_schema()

    def inspect(value):
        if isinstance(value, list):
            for item in value:
                inspect(item)
        elif isinstance(value, dict):
            assert not {"minLength", "maxLength", "pattern", "minItems", "maxItems"}.intersection(value)
            if value.get("type") == "object":
                assert value["additionalProperties"] is False
                assert set(value["required"]) == set(value["properties"])
            for item in value.values():
                inspect(item)

    inspect(schema)
    assert schema["properties"]["claims"]["type"] == "array"


@pytest.mark.parametrize("status,reason", [
    (301, "azure_http"), (400, "azure_bad_request"), (401, "azure_auth"),
    (403, "azure_forbidden"), (404, "azure_deployment"), (408, "azure_timeout"),
    (429, "azure_rate_limit"), (500, "azure_server"), (503, "azure_server"),
])
def test_http_failures_are_classified_without_retry_or_upstream_leaks(status, reason):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(status, headers={"location": "https://elsewhere.invalid"}, json={"error": "private-upstream-detail"})

    provider = AzureTacticalProvider(azure_configuration(settings()), transport=httpx.MockTransport(handle))
    with pytest.raises(ProviderError) as caught:
        provider.generate(facts())
    assert caught.value.reason == reason and len(calls) == 1
    assert "private-upstream-detail" not in str(caught.value)


@pytest.mark.parametrize("error,reason", [(httpx.ReadTimeout, "azure_timeout"), (httpx.ConnectError, "azure_network")])
def test_transport_failures_have_safe_diagnostics(error, reason):
    def handle(request):
        raise error("private-network-detail", request=request)

    provider = AzureTacticalProvider(azure_configuration(settings()), transport=httpx.MockTransport(handle))
    with pytest.raises(ProviderError) as caught:
        provider.generate(facts())
    assert caught.value.reason == reason and "private-network-detail" not in str(caught.value)


@pytest.mark.parametrize("case,reason", [
    ("incomplete", "azure_incomplete"), ("refusal", "azure_refusal"),
    ("no_output", "azure_invalid_response"), ("non_json", "azure_invalid_response"),
    ("invalid_candidate", "azure_invalid_response"), ("unfinished_message", "azure_invalid_response"),
])
def test_unusable_outputs_are_not_published(case, reason):
    body = response_body()
    if case == "incomplete":
        body["status"] = "incomplete"
    elif case == "refusal":
        body["output"][-1]["content"] = [{"type": "refusal", "refusal": "private-refusal"}]
    elif case == "no_output":
        body["output"] = []
    elif case == "unfinished_message":
        body["output"][-1]["status"] = "in_progress"
    elif case == "invalid_candidate":
        body["output"][-1]["content"][0]["text"] = '{"event_id":"evt-064","free_text":"private-prose"}'
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="not-json") if case == "non_json" else httpx.Response(200, json=body))
    provider = AzureTacticalProvider(azure_configuration(settings()), transport=transport)
    with pytest.raises(ProviderError) as caught:
        provider.generate(facts())
    assert caught.value.reason == reason and "private-" not in str(caught.value)


@pytest.mark.parametrize("case", ["success", "conflict", "rate_limit"])
def test_api_reports_actual_azure_execution_rejection_or_mock_fallback(client, case):
    candidate = mock_candidate(facts())
    if case == "conflict":
        next(item for item in candidate.claims if item.field == "lines_broken").value = 9
    transport = httpx.MockTransport(lambda request: httpx.Response(429, json={"error": "private-limit-detail"}) if case == "rate_limit" else httpx.Response(200, json=response_body(candidate)))
    provider = AzureTacticalProvider(azure_configuration(settings()), transport=transport)
    client.app.dependency_overrides[get_provider_selection] = lambda: ProviderSelection(provider, "azure")
    result = client.post("/events/process", json={"match_id": "match-demo-01", "event_id": "evt-064"})
    assert result.status_code == 200
    body = ProcessEventResponse.model_validate(result.json())
    assert body.statistics.pass_length == 44.28 and body.event.lines_broken == 1
    if case == "rate_limit":
        assert body.provider == "fallback" and body.insight is not None
        assert body.agent_trace[1].output["actual_provider"] == "mock"
        assert body.agent_trace[1].output["fallback_reason"] == "azure_rate_limit"
        assert [item["status"] for item in body.agent_trace[1].output["attempts"]] == ["failed", "completed"]
        assert "no model was called" not in " ".join(body.warnings)
    else:
        assert body.provider == "azure" and body.agent_trace[1].output["actual_provider"] == "azure"
        assert "Azure deployment" in body.agent_trace[1].summary
        assert (body.insight is None) == (case == "conflict")
        assert body.validation.status == ("rejected" if case == "conflict" else "validated")
    assert "private-limit-detail" not in result.text and "unit-test-secret" not in result.text


def test_offline_preflight_never_constructs_a_network_provider():
    def unexpected(config):
        raise AssertionError("Offline checks must not create a network client.")

    code, report = check_azure(settings(llm_provider="mock"), provider_factory=unexpected)
    assert code == 0 and report["status"] == "configuration_ready"
    assert report["deployment_access"] == "not_checked" and report["provider_enabled"] is False
    assert "unit-test-secret" not in json.dumps(report)


def test_preflight_reports_missing_fields_without_exposing_values():
    code, report = check_azure(settings(azure_openai_endpoint="", azure_openai_api_key=""))
    assert code == 1 and report["status"] == "configuration_required"
    assert report["deployment_access"] == "not_checked"


@pytest.mark.parametrize("case", ["success", "conflict", "failure"])
def test_live_preflight_uses_no_fallback_and_checks_the_same_trust_contract(case):
    candidate = mock_candidate(facts())
    if case == "conflict":
        candidate.claims.pop()

    def factory(config):
        def handle(request):
            return httpx.Response(401, json={"error": "private-auth-detail"}) if case == "failure" else httpx.Response(200, json=response_body(candidate))
        return AzureTacticalProvider(config, transport=httpx.MockTransport(handle))

    code, report = check_azure(settings(), live=True, provider_factory=factory)
    assert code == (0 if case == "success" else 1)
    assert report["status"] == {"success": "live_verified", "conflict": "candidate_rejected", "failure": "live_failed"}[case]
    assert "private-auth-detail" not in json.dumps(report) and "unit-test-secret" not in json.dumps(report)


def test_cli_settings_errors_print_field_names_only(monkeypatch, capsys):
    monkeypatch.setenv("AZURE_OPENAI_TIMEOUT_SECONDS", "private-invalid-value")
    assert main([]) == 1
    output = capsys.readouterr().out
    assert "settings_invalid" in output and "azure_openai_timeout_seconds" in output
    assert "private-invalid-value" not in output

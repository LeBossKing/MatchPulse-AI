"""Azure OpenAI v1 Responses adapter with structured output and no automatic retries."""

import json

import httpx
from pydantic import ValidationError

from app.agents.contracts import IntelligenceResult, TacticalCandidate
from app.services.azure_config import AzureConfiguration
from app.services.provider_errors import ProviderError

INSTRUCTIONS = """You are the MatchPulse Tactical Explainer for synthetic football events.
Return a structured tactical candidate for the supplied canonical event only.
Copy EVERY supplied evidence item exactly once, retaining its ID, source, field,
primitive JSON type, and value. Do not invent facts, change values, or omit claims.
Select interpretation: interception/recovery => regain; unsuccessful pass =>
attempt_failed; completed pass with forward_progression > 0 => advance;
other completed passes => retain.
Select importance using these explicit demo rules: regains => medium;
unsuccessful passes => low; completed passes with progression >= 20 and at least
one annotated line broken => high; other completed passes with progression >= 15
=> medium; other passes => low. Missing annotations remain unknown.
Coordinates are normalized, not metres. Do not infer defender positions,
specific midfield lines, goals, or subsequent chances. Supply no narrative prose.
"""

# Azure's structured-output subset excludes these validation keywords. The full
# Pydantic contract and trust stage still enforce their constraints after parsing.
UNSUPPORTED_SCHEMA_KEYS = {
    "minLength", "maxLength", "pattern", "format", "minimum", "maximum",
    "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "minItems", "maxItems",
    "uniqueItems", "minProperties", "maxProperties", "default", "title",
}


def candidate_schema() -> dict:
    def compatible(value):
        if isinstance(value, list):
            return [compatible(item) for item in value]
        if not isinstance(value, dict):
            return value
        result = {key: compatible(item) for key, item in value.items() if key not in UNSUPPORTED_SCHEMA_KEYS}
        if result.get("type") == "object":
            result["additionalProperties"] = False
            result["required"] = list(result.get("properties", {}))
        return result

    return compatible(TacticalCandidate.model_json_schema())


def response_candidate(body: object) -> TacticalCandidate:
    if not isinstance(body, dict):
        raise ProviderError(reason="azure_invalid_response")
    if body.get("status") != "completed":
        raise ProviderError(reason="azure_incomplete")
    output = body.get("output")
    if not isinstance(output, list):
        raise ProviderError(reason="azure_invalid_response")
    texts = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue  # Reasoning and future extra output types are not narrative claims.
        if item.get("role") != "assistant" or item.get("status") != "completed":
            raise ProviderError(reason="azure_invalid_response")
        content = item.get("content")
        if not isinstance(content, list):
            raise ProviderError(reason="azure_invalid_response")
        for part in content:
            if not isinstance(part, dict):
                raise ProviderError(reason="azure_invalid_response")
            if part.get("type") == "refusal":
                raise ProviderError(reason="azure_refusal")
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                texts.append(part["text"])
    text = "".join(texts).strip()
    if not text or len(text) > 65536:
        raise ProviderError(reason="azure_invalid_response")
    try:
        return TacticalCandidate.model_validate_json(text)
    except ValidationError:
        raise ProviderError(reason="azure_invalid_response") from None


class AzureTacticalProvider:
    name = "azure"

    def __init__(self, config: AzureConfiguration, *, transport: httpx.BaseTransport | None = None):
        self.config = config
        self.transport = transport

    def generate(self, facts: IntelligenceResult) -> TacticalCandidate:
        config = self.config
        payload = {
            "model": config.deployment,
            "instructions": INSTRUCTIONS,
            "input": json.dumps({
                "event": facts.event.model_dump(mode="json"),
                "statistics": facts.statistics.model_dump(mode="json"),
                "evidence": [item.model_dump(mode="json") for item in facts.evidence],
            }, ensure_ascii=False),
            "text": {"format": {
                "type": "json_schema", "name": "tactical_candidate",
                "strict": True, "schema": candidate_schema(),
            }},
            "max_output_tokens": config.max_output_tokens,
            "store": False,
        }
        timeout = httpx.Timeout(config.timeout_seconds, connect=min(5, config.timeout_seconds))
        try:
            with httpx.Client(timeout=timeout, follow_redirects=False, transport=self.transport) as client:
                response = client.post(
                    config.base_url + "responses", json=payload,
                    headers={"api-key": config.api_key.get_secret_value()},
                )
        except httpx.TimeoutException:
            raise ProviderError(reason="azure_timeout") from None
        except httpx.RequestError:
            raise ProviderError(reason="azure_network") from None
        code = response.status_code
        reasons = {
            400: "azure_bad_request", 401: "azure_auth", 403: "azure_forbidden",
            404: "azure_deployment", 408: "azure_timeout", 429: "azure_rate_limit",
        }
        if code != 200:
            reason = reasons.get(code, "azure_server" if code >= 500 else "azure_http")
            raise ProviderError(reason=reason)
        try:
            body = response.json()
        except ValueError:
            raise ProviderError(reason="azure_invalid_response") from None
        return response_candidate(body)

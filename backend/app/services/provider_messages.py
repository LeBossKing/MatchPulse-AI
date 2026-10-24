"""Public diagnostic hints keyed by safe error codes, never upstream error text."""

HINTS = {
    "azure_configuration": "Azure settings are incomplete or invalid. Run python scripts/check_azure.py.",
    "azure_timeout": "Azure timed out. Check connectivity and deployment availability before retrying.",
    "azure_network": "Azure could not be reached. Check DNS, proxy, and resource network access.",
    "azure_auth": "Azure rejected authentication. Check the resource key and endpoint pairing.",
    "azure_forbidden": "Azure denied access. Check permissions, key-auth policy, and resource network rules.",
    "azure_deployment": "Azure could not find the deployment. Check the deployment name and resource endpoint.",
    "azure_rate_limit": "Azure reported a rate or quota limit. Check this deployment's available quota.",
    "azure_bad_request": "Azure rejected the request. Check model support for Responses and structured outputs.",
    "azure_server": "Azure returned a service error. Check deployment availability before retrying.",
    "azure_http": "Azure returned an unexpected HTTP status. Check the configured resource endpoint.",
    "azure_incomplete": "Azure did not complete the output. Check the model and output-token limit.",
    "azure_refusal": "Azure declined to produce a candidate. No explanation from that response was published.",
    "azure_invalid_response": "Azure returned an unusable candidate structure. Check model compatibility.",
    "provider_error": "The provider failed or returned an invalid structure.",
}


def provider_hint(reason: str) -> str:
    return HINTS.get(reason, HINTS["provider_error"])

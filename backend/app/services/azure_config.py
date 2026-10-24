"""Validate backend Azure settings without making a network request or echoing secrets."""

from dataclasses import dataclass
import re
from urllib.parse import urlsplit

from pydantic import SecretStr

from app.config import Settings

HOST = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}\.(?:openai\.azure\.com|services\.ai\.azure\.com)$")
DEPLOYMENT = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}$")


class AzureConfigurationError(Exception):
    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("Azure configuration is incomplete or invalid.")


@dataclass(frozen=True)
class AzureConfiguration:
    base_url: str
    deployment: str
    api_key: SecretStr
    timeout_seconds: float
    max_output_tokens: int


def azure_configuration(settings: Settings) -> AzureConfiguration:
    issues = []
    endpoint = settings.azure_openai_endpoint.strip()
    base_url = ""
    if not endpoint:
        issues.append("Set AZURE_OPENAI_ENDPOINT to your resource endpoint.")
    else:
        try:
            url = urlsplit(endpoint)
            valid = (
                url.scheme == "https" and url.hostname is not None
                and HOST.fullmatch(url.hostname) is not None
                and url.username is None and url.password is None
                and url.port in (None, 443) and not url.query and not url.fragment
                and url.path.rstrip("/") in ("", "/openai/v1")
            )
            if not valid:
                raise ValueError("Unsupported endpoint shape.")
            base_url = f"https://{url.hostname}/openai/v1/"
        except ValueError:
            issues.append(
                "AZURE_OPENAI_ENDPOINT must be an HTTPS resource URL on openai.azure.com "
                "or services.ai.azure.com, optionally ending in /openai/v1/."
            )
    deployment = settings.azure_openai_deployment.strip()
    if not DEPLOYMENT.fullmatch(deployment):
        issues.append("Set AZURE_OPENAI_DEPLOYMENT to the deployment name from Foundry.")
    secret = settings.azure_openai_api_key
    key = secret.get_secret_value().strip() if secret else ""
    if not key or key.lower() in {"your-api-key", "replace-me", "<your-api-key>"}:
        issues.append("Set AZURE_OPENAI_API_KEY in backend/.env or the backend environment.")
    if issues:
        raise AzureConfigurationError(issues)
    return AzureConfiguration(
        base_url=base_url, deployment=deployment, api_key=SecretStr(key),
        timeout_seconds=settings.azure_openai_timeout_seconds,
        max_output_tokens=settings.azure_openai_max_output_tokens,
    )

"""Check Azure configuration offline; --live sends one request without mock fallback."""

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from pydantic import ValidationError  # noqa: E402

from app.agents.match_intelligence import analyze_event  # noqa: E402
from app.agents.trust_personalization import validate_and_personalize  # noqa: E402
from app.config import Settings  # noqa: E402
from app.services.azure_config import AzureConfigurationError, azure_configuration  # noqa: E402
from app.services.azure_openai import AzureTacticalProvider  # noqa: E402
from app.services.demo_repository import FixtureLoadError, load_demo_fixture  # noqa: E402
from app.services.provider_errors import ProviderError  # noqa: E402
from app.services.provider_messages import provider_hint  # noqa: E402


def check_azure(settings: Settings, *, live: bool = False, provider_factory=AzureTacticalProvider) -> tuple[int, dict]:
    report = {
        "check": "azure_openai", "live_requested": live,
        "deployment_access": "not_checked", "provider_enabled": settings.llm_provider == "azure",
    }
    try:
        config = azure_configuration(settings)
    except AzureConfigurationError as error:
        return 1, report | {"status": "configuration_required", "issues": error.issues}
    if not live:
        return 0, report | {
            "status": "configuration_ready",
            "message": "Local settings are valid. Azure access has not been tested. Run with --live for one request.",
        }
    try:
        fixture = load_demo_fixture()
        index = next(i for i, event in enumerate(fixture.events) if event.event_id == fixture.main_event_id)
        facts = analyze_event(fixture, index)
        started = perf_counter()
        candidate = provider_factory(config).generate(facts)
        trusted = validate_and_personalize(fixture, facts, candidate, "analyst", "en")
        elapsed = round((perf_counter() - started) * 1000, 2)
    except ProviderError as error:
        return 1, report | {
            "status": "live_failed", "reason": error.reason, "message": provider_hint(error.reason),
            "message_note": "No mock fallback is used by this check.",
        }
    except (FixtureLoadError, ValidationError):
        return 1, report | {"status": "local_data_invalid", "message": "Check the local canonical fixture and response models."}
    report = report | {
        "deployment_access": "verified", "provider": "azure", "elapsed_ms": elapsed,
        "event_id": fixture.main_event_id, "evidence_count": len(facts.evidence),
        "validation_status": trusted.validation.status,
    }
    if trusted.insight is None:
        return 1, report | {
            "status": "candidate_rejected",
            "message": "Azure responded, but its structured claims failed the local trust checks.",
        }
    return 0, report | {
        "status": "live_verified",
        "message": "One Azure structured-output request passed the local trust checks. Balance and quota inventory were not queried.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send one model request; uses your deployment's tokens.")
    args = parser.parse_args(argv)
    try:
        settings = Settings()
    except ValidationError as error:
        fields = sorted({str(item["loc"][0]) for item in error.errors() if item["loc"]})
        print(json.dumps({
            "status": "settings_invalid", "fields": fields,
            "message": "Fix the listed backend settings. Input values are omitted.",
        }, indent=2))
        return 1
    code, report = check_azure(settings, live=args.live)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

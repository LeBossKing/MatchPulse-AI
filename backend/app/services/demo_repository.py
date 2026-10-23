"""Read the canonical synthetic fixture without mutating match state."""

from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError

from app.models.match import DemoFixture

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "data" / "demo_match.json"


class FixtureLoadError(Exception):
    pass


@lru_cache(maxsize=1)
def load_demo_fixture() -> DemoFixture:
    try:
        return DemoFixture.model_validate_json(FIXTURE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, ValidationError) as error:
        raise FixtureLoadError("The synthetic demo fixture could not be loaded.") from error

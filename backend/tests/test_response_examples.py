from copy import deepcopy
import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.insight import ProcessEventResponse
from app.services.demo_repository import load_demo_fixture

EXAMPLES = Path(__file__).resolve().parents[1] / "data" / "examples"
RESPONSE_FILES = sorted(path for path in EXAMPLES.glob("*.json") if path.name != "process-request.json")


@pytest.mark.parametrize("path", RESPONSE_FILES, ids=lambda path: path.stem)
def test_examples_match_source_geometry_and_prefix_totals(path):
    response = ProcessEventResponse.model_validate_json(path.read_text())
    assert response.result_source == "example" and response.provider == "mock"
    fixture = load_demo_fixture()
    index = next(i for i, event in enumerate(fixture.events) if event.event_id == response.event_id)
    assert response.event == fixture.events[index]
    prefix = fixture.events[:index + 1]
    assert response.match_statistics.event_count == len(prefix)
    for team in response.match_statistics.teams:
        passes = [event for event in prefix if event.team_id == team.team_id and event.event_type == "pass"]
        assert team.passes_attempted == len(passes)
        assert team.passes_completed == sum(event.successful for event in passes)
    if response.event.event_type == "pass":
        event = response.event
        assert response.statistics.pass_length == round(
            math.hypot(event.end.x - event.start.x, event.end.y - event.start.y), 2
        )
        direction = 1 if event.attacking_direction == "left_to_right" else -1
        assert response.statistics.forward_progression == round(
            direction * (event.end.x - event.start.x), 2
        )


@pytest.mark.parametrize("case", [
    "missing_evidence", "wrong_evidence_value", "wrong_overlay", "wrong_event_id",
    "wrong_trace_order", "duplicate_evidence", "unknown_annotation",
])
def test_response_rejects_misleading_structure(case):
    data = json.loads((EXAMPLES / "main-analyst-en.json").read_text())
    data = deepcopy(data)
    if case == "missing_evidence":
        data["insight"]["evidence_ids"].append("missing")
    elif case == "wrong_evidence_value":
        data["evidence"][0]["value"] = False
    elif case == "wrong_overlay":
        data["overlay"]["end"]["x"] = 99
    elif case == "wrong_event_id":
        data["event_id"] = "different-event"
    elif case == "wrong_trace_order":
        data["agent_trace"].reverse()
    elif case == "duplicate_evidence":
        data["evidence"].append(data["evidence"][0])
    elif case == "unknown_annotation":
        data["event"]["pressure"] = None
    with pytest.raises(ValidationError):
        ProcessEventResponse.model_validate(data)


def test_personalization_keeps_identical_source_facts():
    variants = [
        ProcessEventResponse.model_validate_json(path.read_text())
        for path in sorted(EXAMPLES.glob("main-*.json"))
    ]
    assert len(variants) == 4
    for variant in variants[1:]:
        assert variant.event == variants[0].event
        assert variant.statistics == variants[0].statistics
        assert variant.match_statistics == variants[0].match_statistics
        assert variant.evidence == variants[0].evidence
    assert len({variant.insight.explanation for variant in variants}) == 4

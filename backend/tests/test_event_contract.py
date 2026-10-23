from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.models.event import MatchEvent
from app.models.match import DemoFixture, TeamStatistics


def test_fixture_main_event_is_the_agreed_forward_pass(fixture_data):
    fixture = DemoFixture.model_validate(fixture_data)
    main = next(event for event in fixture.events if event.event_id == fixture.main_event_id)
    assert main.event_type == "pass" and main.successful
    assert main.start.x == 27 and main.end.x == 67
    assert main.pressure == "high" and main.lines_broken == 1
    assert fixture.review_status == "pending_review"


@pytest.mark.parametrize("field,value", [
    ("minute", -1), ("minute", 151), ("second", 60), ("second", 1.5),
    ("second", True), ("period", 3), ("successful", "true"),
    ("event_type", "shot"), ("pressure", "unknown"), ("lines_broken", -1),
])
def test_event_rejects_invalid_values(fixture_data, field, value):
    event = deepcopy(fixture_data["events"][3])
    event[field] = value
    with pytest.raises(ValidationError):
        MatchEvent.model_validate(event)


@pytest.mark.parametrize("value", [-1, 101, "27", True, float("nan"), float("inf")])
def test_coordinates_reject_invalid_values(fixture_data, value):
    event = deepcopy(fixture_data["events"][3])
    event["start"]["x"] = value
    with pytest.raises(ValidationError):
        MatchEvent.model_validate(event)


@pytest.mark.parametrize("field", ["event_id", "match_id", "start", "end", "target_player_id"])
def test_completed_pass_requires_its_fields(fixture_data, field):
    event = deepcopy(fixture_data["events"][3])
    event.pop(field)
    with pytest.raises(ValidationError):
        MatchEvent.model_validate(event)


def test_missing_annotations_stay_unknown(fixture_data):
    event = MatchEvent.model_validate(fixture_data["events"][6])
    assert event.pressure is None and event.lines_broken is None
    assert event.attacking_direction == "right_to_left"


def test_unsuccessful_pass_cannot_claim_completed_lines_broken(fixture_data):
    event = deepcopy(fixture_data["events"][4])
    event["lines_broken"] = 1
    with pytest.raises(ValidationError):
        MatchEvent.model_validate(event)


@pytest.mark.parametrize("field,value", [
    ("successful", False), ("end", {"x": 1, "y": 1}),
    ("target_player_id", "harbor-08"), ("lines_broken", 0),
])
def test_regains_have_point_event_semantics(fixture_data, field, value):
    event = deepcopy(fixture_data["events"][5])
    event[field] = value
    with pytest.raises(ValidationError):
        MatchEvent.model_validate(event)


def test_unknown_event_fields_are_rejected(fixture_data):
    event = deepcopy(fixture_data["events"][3])
    event["confidence_score"] = 0.99
    with pytest.raises(ValidationError):
        MatchEvent.model_validate(event)


@pytest.mark.parametrize("case", [
    "duplicate_event", "unknown_player", "opponent_receiver",
    "wrong_match", "unknown_team", "out_of_order", "direction_change", "same_direction",
])
def test_fixture_rejects_internal_inconsistencies(fixture_data, case):
    data = deepcopy(fixture_data)
    if case == "duplicate_event":
        data["events"][1]["event_id"] = data["events"][0]["event_id"]
    elif case == "unknown_player":
        data["events"][0]["player_id"] = "missing-player"
    elif case == "opponent_receiver":
        data["events"][0]["target_player_id"] = "harbor-08"
    elif case == "wrong_match":
        data["events"][0]["match_id"] = "other-match"
    elif case == "unknown_team":
        data["events"][0]["team_id"] = "third-team"
    elif case == "out_of_order":
        data["events"][0], data["events"][1] = data["events"][1], data["events"][0]
    elif case == "direction_change":
        data["events"][0]["attacking_direction"] = "right_to_left"
    elif case == "same_direction":
        for event in data["events"]:
            event["attacking_direction"] = "left_to_right"
    with pytest.raises(ValidationError):
        DemoFixture.model_validate(data)


def test_accuracy_is_null_before_any_pass():
    assert TeamStatistics(team_id="atlas").pass_accuracy_pct is None
    with pytest.raises(ValidationError):
        TeamStatistics(team_id="atlas", pass_accuracy_pct=0)


def test_accuracy_must_match_recorded_totals():
    with pytest.raises(ValidationError):
        TeamStatistics(
            team_id="atlas", passes_attempted=5, passes_completed=4, pass_accuracy_pct=100
        )
    stats = TeamStatistics(
        team_id="atlas", passes_attempted=5, passes_completed=4, pass_accuracy_pct=80
    )
    assert stats.pass_accuracy_pct == 80

from itertools import product

from scripts.export_dashboard_samples import sample_document


def test_dashboard_samples_cover_every_event_and_setting_without_claiming_live_execution():
    document = sample_document()
    events = document["events"]["events"]
    expected = set(product((event["event_id"] for event in events), ("en", "fr"), ("analyst", "fan")))
    actual = {(item["event_id"], item["language"], item["audience"]) for item in document["responses"]}
    assert actual == expected and len(document["responses"]) == 32
    for response in document["responses"]:
        assert response["result_source"] == "example" and response["provider"] == "mock"
        assert response["warnings"] and all(step["duration_ms"] == 0 for step in response["agent_trace"])
        assert all("no agent executes in the browser" in step["summary"] for step in response["agent_trace"])
    assert document["match"]["statistics"]["event_count"] == 0


def test_sample_exports_are_deterministic_and_preferences_preserve_facts():
    document = sample_document()
    assert sample_document() == document
    for event in document["events"]["events"]:
        variants = [item for item in document["responses"] if item["event_id"] == event["event_id"]]
        for variant in variants[1:]:
            for field in ("event", "statistics", "match_statistics", "evidence", "overlay"):
                assert variant[field] == variants[0][field]

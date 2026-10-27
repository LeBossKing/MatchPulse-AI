# Proposed story API contract

**Not implemented or endorsed by Member 1 yet.** Existing MVP uses `POST /events/process`; agree whether to add `POST /stories/process` or extend existing endpoint. The JSON example is a proposal, not a recorded backend response.

`match_id`, `story_id`, `audience` (`fan` / `analyst`) and `language` (`en` / `fr`) are request fields. Response must include exact source `event_ids`, structured `facts`, explanation, source-backed `evidence`, validation status/warnings, and actual agent execution trace. Use actual `not_run` or `skipped` states, never fabricate a completed execution.

Error conditions: missing story => 404; malformed request => 422; provider outage => disclosed fallback with `generation_mode=mock`, not success falsely labelled Azure. Member 1 must confirm names, types and response design.

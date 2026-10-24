# MatchPulse AI API contract v1

Contract/schema version: **1.0.0**. Backend application version: **0.4.0**.
Status: implemented technical contract; synthetic fixture and tactical annotations await Member 2 review.

## Endpoint status

| Method and route | Current behavior |
| --- | --- |
| `GET /health` | 200, public API metadata. Does not verify Azure. |
| `GET /matches/demo` | 200, synthetic match metadata and initial zeroed sequence statistics. |
| `GET /matches/demo/events` | 200, the eight canonical events and main event ID. |
| `POST /events/process` | **200** for a processed canonical event, 422 for invalid input, 404 for unknown IDs, and structured 500 errors for invalid fixtures or an unavailable workflow. |

Swagger: <http://127.0.0.1:8000/docs>. OpenAPI: <http://127.0.0.1:8000/openapi.json>.
The committed [OpenAPI export](openapi.json) is generated from the application. All business envelopes use `schema_version`; the health endpoint keeps its existing simple shape.

## Coordinates and event semantics

- Coordinates are finite JSON numbers in `[0, 100]`, measured in normalized pitch units, with origin at the top left. X increases left to right; Y increases top to bottom.
- These values are **not metres**. No pitch dimensions or physical distances are inferred.
- Every event explicitly states `attacking_direction`: `left_to_right` or `right_to_left`.
- `minute` is absolute elapsed match time, integer 0-150; `second` is integer 0-59. `period` is integer 1 or 2. List order breaks ties at the same timestamp.
- IDs contain letters, digits, underscores, or hyphens, start with a letter/digit, and have at most 64 characters.
- Supported MVP event types are `pass`, `interception`, and `recovery`. Shots and goals require a later contract extension.
- Passes require `start` and `end`. The end point is the recorded ball endpoint, not an inferred receiver position. `target_player_id` identifies the intended receiver, including for failed attempts. Completed passes require that receiver on the same team, different from the passer.
- Interceptions and recoveries represent completed regains: `successful` is true, with a start point, no end point, and no receiver.
- `pressure` is optional: `low`, `medium`, `high`, or null/omitted for unknown.
- `lines_broken` is an optional nonnegative integer for passes. Positive values describe completed passes only. Explicit zero means zero recorded lines; null/omitted means unknown.
- Pressure and lines broken are **authored synthetic annotations**, not conclusions calculated from the pass coordinates.
- Unknown fields, string-valued numbers, boolean coordinates/counts, contradictory regains, invalid rosters, repeated event IDs, inconsistent directions, and unordered fixtures are rejected by Pydantic.

The exported JSON Schemas describe field shapes and ranges. Pydantic additionally enforces semantic relationships across fields and evidence; use the backend validators for full validation.

## Canonical event example

```json
{
  "event_id": "evt-064",
  "match_id": "match-demo-01",
  "period": 2,
  "minute": 63,
  "second": 24,
  "event_type": "pass",
  "team_id": "atlas",
  "player_id": "player-07",
  "target_player_id": "player-11",
  "attacking_direction": "left_to_right",
  "start": {"x": 27, "y": 58},
  "end": {"x": 67, "y": 39},
  "successful": true,
  "pressure": "high",
  "lines_broken": 1
}
```

Expected example facts: pass length `round(sqrt(40² + 19²), 2) = 44.28`; forward progression `+40`. For right-to-left attacks, progression is `start.x - end.x`. Neither calculation establishes defensive player positions or a subsequent chance.

## Selecting an event for processing

```bash
curl -X POST http://127.0.0.1:8000/events/process \
  -H 'Content-Type: application/json' \
  -d '{"match_id":"match-demo-01","event_id":"evt-064","audience":"analyst","language":"en"}'
```

```json
{
  "match_id": "match-demo-01",
  "event_id": "evt-064",
  "audience": "analyst",
  "language": "en"
}
```

`audience` defaults to `analyst`; `language` defaults to `en`. Supported values are `fan`/`analyst` and `en`/`fr`. The client submits identifiers and preferences, not replacement event facts. The backend looks up its canonical source event.

Current response for the valid request above: **200**, with `result_source: runtime`, calculated statistics, evidence, validation, and actual stage traces. Default `LLM_PROVIDER=mock` runs locally. A configured `azure` provider calls one deployment for a structured candidate; calculations, trust checks, and final narrative templates remain local. A processed result can carry `validation.status: rejected` and `insight: null` if its candidate conflicts with evidence.

Azure configuration or provider failures use a visible mock fallback (`provider: fallback`) with a safe `fallback_reason` in the tactical trace. Successful Azure execution uses `provider: azure`; HTTP 200 alone does not verify deployment access. Use the no-fallback live preflight in [Azure setup](azure-setup.md).

## Successful processing response

The 200 response contains:

| Field | Meaning |
| --- | --- |
| `schema_version`, `status` | Contract version and `processed`; processing completion does not by itself mean an insight was accepted. |
| `result_source` | `runtime` for an actual workflow run; `example` for checked-in illustrative fixtures. |
| `data_source`, `review_status` | Synthetic-data provenance and review status. |
| `match_id`, `event_id`, `event` | Consistent identifiers and the canonical selected event. |
| `audience`, `language`, `provider` | Selected presentation preferences and actual provider (`mock`, `azure`, or `fallback`). |
| `statistics` | `units`, nullable `pass_length`, nullable `forward_progression`. Pass metrics are null for point events. |
| `match_statistics` | Statistics for the sequence prefix ending at this event; never whole-match totals. |
| `insight` | Title, explanation, separately labelled interpretation, qualitative importance, and evidence IDs. Null if rejected. |
| `evidence` | Unique IDs, source (`event` or `statistics`), dot-separated field paths, and exact primitive source values. |
| `validation` | `validated`, `limited`, or `rejected`, plus unsupported claims and limitations. No invented confidence percentage. |
| `overlay` | A pass trajectory or point marker matching the selected event's coordinates. |
| `agent_trace` | Exactly three ordered roles, each with status, duration, summary, and inspectable JSON output. |
| `warnings` | Visible caveats; a fallback requires a warning. |

Trace order: `match_intelligence`, `tactical_explainer`, `trust_personalization`. Final step statuses are `completed`, `skipped`, or `failed`; the UI can show loading locally while awaiting the REST response.

The schema checks IDs, coordinate overlays, evidence availability and values, evidence references, trace order, and validation/insight consistency. The local trust stage additionally checks each candidate claim, interpretation category, and importance heuristic before rendering controlled templates for either provider. It does not accept or fact-check arbitrary provider-authored prose. Member 2 still reviews the annotations and tactical interpretation. See [workflow design](mock-workflow.md).

### Complete response examples

- [Analyst / English](../backend/data/examples/main-analyst-en.json)
- [Fan / English](../backend/data/examples/main-fan-en.json)
- [Analyst / French](../backend/data/examples/main-analyst-fr.json)
- [Fan / French](../backend/data/examples/main-fan-fr.json)
- [Failed pass](../backend/data/examples/unsuccessful-pass.json)
- [Missing tactical annotations](../backend/data/examples/missing-annotations.json)
- [Interception](../backend/data/examples/interception.json)
- [Recovery](../backend/data/examples/recovery.json)

These historical contract examples carry `result_source: "example"`, zero placeholder durations, and explicit warnings. They have not been generated by executed agents. Runtime responses compute the same source facts afresh, may use different wording or additional evidence, and contain actual measured traces.

## Statistics and replay invariants

- Pass accuracy is `round(100 * completed / attempted, 2)`; it is null before any pass attempts.
- `GET /matches/demo` always returns the initial pre-replay state: zero counts, null accuracy, and null `through_event_id`.
- Processing statistics describe the canonical prefix through the selected event, identified by `through_event_id`, with `scope: demo_sequence`.
- Selecting the same event again, changing audience/language, or rewinding must not increment counters. Task 4 computes each prefix rather than mutating a global match counter.
- The sequence is 63:08-63:38 with a partial roster. It supplies no earlier match history or full-match possession percentage.

## Errors

```json
{
  "schema_version": "1.0.0",
  "error": {
    "code": "invalid_request",
    "message": "The request does not match the API contract.",
    "details": [
      {"field":"body.audience","message":"Unsupported value","type":"literal_error"}
    ]
  }
}
```

Validation messages can differ by Pydantic version; clients use `code`, status, and `details[].field`. Input values are not echoed.

| HTTP status | Code | Meaning |
| --- | --- | --- |
| 404 | `match_not_found` / `event_not_found` | Selector does not exist. |
| 404 | `not_found` | Unknown route. |
| 422 | `invalid_request` | Missing, malformed, extra, or invalid request fields. |
| 500 | `invalid_fixture` | Canonical dataset cannot be loaded or validated. |
| 500 | `processing_failed` | The provider and mock fallback could not produce a usable candidate. |

## Contract generation

Pydantic models are the source of truth. Run `python scripts/export_contract.py` from `backend/`, then `npm run generate:api` from `frontend/`. Commit all outputs together.

Browser runtime validation uses the generated `frontend/src/api/generated-schemas.json` bundle and adds selection/source consistency checks. It complements backend validation. The exporter includes [match read response](schemas/demo-match-response.schema.json) and [events read response](schemas/demo-events-response.schema.json).

Formal schemas: [event](schemas/event.schema.json), [fixture](schemas/demo-fixture.schema.json), [request](schemas/process-request.schema.json), [response](schemas/process-response.schema.json). Generated TypeScript lives in `frontend/src/types/generated-api.d.ts`; named aliases live in `types/api.ts` and `types/match.ts`.

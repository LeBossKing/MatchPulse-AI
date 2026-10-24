# Architecture

## Implemented through Task 6

React/TypeScript/Vite renders the match dashboard from checked-in sample responses. Its API URL remains available for the optional backend health panel; processing REST calls follow in Task 7. Backend configuration and Azure credentials stay on the server.

The dashboard has a source-coordinate SVG pitch, prefix history trails, an eight-event timeline, timed replay, seeking, filters, an insight/evidence/trust panel, prefix team statistics, and expandable sample stage outputs. Presentation preferences select among the 32 typed examples without changing event facts. Filters change only the visible timeline, not the selected event or its canonical prefix totals. Replay uses source timestamp gaps divided by the selected speed, and stops at the final event. Manual selection, seeking, and reset pause playback.

`export_dashboard_samples.py` runs the mock workflow at authoring time for every event/language/audience combination, revalidates each response, replaces durations with zero placeholders, and marks every result as `example`. The browser displays persistent sample provenance and never claims these are live timings or agent runs. The generator's `--check` mode detects stale exports. The sample dashboard works without a backend; the health panel mounts only when opened.

FastAPI exposes health, synthetic match metadata, canonical events, and event processing. The fixture repository validates the data with Pydantic, caches it per process, and returns typed read responses without mutating replay state. Invalid requests, fixture-load errors, and unavailable workflows use a common JSON error envelope.

The processing route resolves an ID-based selector against the canonical fixture and executes three request-local stages:

1. **Match Intelligence** copies the selected event, calculates geometry and prefix statistics, and constructs exact source evidence and the overlay.
2. **Tactical Explainer** calls a provider with an isolated snapshot. Either deterministic mock rules or an Azure deployment proposes structured claims, a constrained interpretation category, and a heuristic importance value.
3. **Trust & Personalization** checks the candidate against the trusted facts and rules. It rejects conflicting claims or renders controlled templates for the requested audience and language.

The orchestrator records actual elapsed stage durations, summaries, and intermediate JSON outputs. A runtime result uses `result_source: runtime`; its provider is `mock`, `azure`, or `fallback`. Default mock processing makes no external request. Historical UI fixtures retain `result_source: example`.

The Azure adapter sends one HTTPS request to `/openai/v1/responses`, using the configured deployment name, `text.format` JSON Schema, and `store: false`. It accepts only a completed, parseable structured candidate. The wire schema uses Azure's supported subset; full Pydantic validation and local trust checks still enforce the source contract. It does not request or publish free-form model narrative. There are no automatic retries.

Missing or invalid Azure settings select a visible mock fallback without a network request. Authentication, quota, network, timeout, refusal, and malformed-output failures also use a labelled fallback, with safe reason codes and actual attempt provenance. Structurally valid conflicting claims are rejected by trust rather than replaced. Upstream error bodies and credential values are excluded from client diagnostics.

`check_azure.py` validates settings offline by default. Its explicit `--live` mode sends one actual request without fallback and checks the returned candidate against trusted facts. This can establish deployment access, but does not query subscription balances or quota inventory. The user's subscription remains unverified until that live check is run successfully.

The source fixture is read-only. Prefix statistics are computed afresh for each selection so repeated selection, rewinding, parallel requests, and personalization cannot double-count events. Providers cannot mutate the trusted context or the cached fixture.

Separate known facts from interpretation. Coordinates alone do not establish defender positions, pressure, lines bypassed, shot quality, or a subsequent chance. Pressure and line-break annotations are explicitly authored synthetic data. The trust stage checks structured claims and approved templates; it is not a general semantic fact checker. No invented confidence score is part of the contract.

Pydantic/FastAPI are the contract source of truth. A script exports JSON Schemas and OpenAPI. A pinned isolated OpenAPI TypeScript CLI generates checked-in browser types from that export. Generation needs no running backend or Azure credentials.

## Remaining integration

Complete the account-specific steps in [Azure setup](azure-setup.md). The adapter and offline tests do not establish the user's deployment access.

Named TypeScript aliases expose the generated schema types. The dashboard uses those response types today; frontend calls to the new routes follow in Task 7. The optional health connection check still handles unavailable backends, invalid health responses, timeout, and retry.

See [mock workflow rules and acceptance checks](mock-workflow.md) for implementation details and limits.

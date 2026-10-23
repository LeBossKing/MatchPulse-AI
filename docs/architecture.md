# Architecture

## Implemented through Task 3

React/TypeScript/Vite retains the foundation connection screen. Its public API URL points to FastAPI. Backend configuration and future Azure credentials stay on the server.

FastAPI exposes health, synthetic match metadata, and canonical events. The fixture repository validates the data with Pydantic, caches it per process, and returns typed read responses without mutating replay state. Invalid requests and fixture-load errors use a common JSON error envelope.

The processing route validates an ID-based selector against the canonical fixture. It currently returns 501. Its success response model defines the interface for Task 4; it does not execute agents or return static examples as live results.

Pydantic/FastAPI are the contract source of truth. A script exports JSON Schemas and OpenAPI. A pinned isolated OpenAPI TypeScript CLI generates checked-in browser types from that export. Generation needs no running backend or Azure credentials. Backend tests validate source data, schema relationships, and illustrative responses.

## Next: Task 4 workflow

1. Resolve the canonical source event and the selected sequence prefix.
2. Match Intelligence calculates deterministic geometry and prefix statistics.
3. Tactical Explainer creates a grounded candidate through a mock or Azure provider.
4. Trust & Personalization checks claims and adapts the text to the selected audience and language.
5. Return the final response with actual trace records, provider, evidence, limitations, and provenance.

The source fixture is read-only. Compute prefix statistics afresh for each selection so repeated selection, rewinding, and personalization cannot double-count events. Keep per-request workflow state isolated.

Separate known facts from interpretation. Coordinates alone do not establish player positions, pressure, lines bypassed, shot quality, or a subsequent chance. Pressure and line-break annotations are explicitly authored synthetic data.

A real run uses `result_source: runtime`; UI fixtures use `example`. A fallback must carry a warning. No invented confidence score is part of the contract.

## Frontend work

Named TypeScript aliases expose the generated schema types. The match dashboard and calls to the new routes will be wired in the later frontend/integration tasks. The current health connection check still handles unavailable backends, invalid health responses, timeout, and retry.

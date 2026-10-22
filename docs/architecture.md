# Architecture

## Implemented foundation

The React/TypeScript frontend runs on `http://localhost:5173`. A typed API client requests `GET /health` from FastAPI on `http://127.0.0.1:8000`.

The frontend validates the response shape and distinguishes checking, connected, and offline states. Requests time out after five seconds. A cancelled request cannot overwrite the result of a later connection check.

FastAPI validates its settings with Pydantic Settings and loads `backend/.env` using an absolute path. CORS permits local development origins and the configured `FRONTEND_ORIGIN`. The health response contains only public service metadata.

This checkpoint has no database, match-processing endpoint, or live model calls.

## Planned event-processing workflow

1. Validate the selected synthetic event and audience/language preferences.
2. Match Intelligence computes deterministic statistics and structured evidence.
3. Tactical Explainer produces a grounded narrative through an interchangeable mock or Azure provider.
4. Trust & Personalization checks supported claims and prepares the audience-specific response.
5. Return the selected event, explanation, evidence, validation result, limitations, and real execution trace to React.

The orchestrator will keep request state isolated, record actual execution steps, and handle model failures with an explicitly labelled fallback. The final event and response models are agreed in Task 3.

Pressure and defensive-line claims need source annotations or suitable tracking evidence. Normalized coordinates alone establish geometry, not defender positions. All derived distances must state their units.

## Configuration boundary

Azure credentials belong exclusively in backend settings. The browser receives a public API URL via `VITE_API_BASE_URL`. Provider selection does not establish that a model is deployed or accessible; Azure must be verified separately.

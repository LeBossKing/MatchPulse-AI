# MatchPulse AI

Agentic AI prototype transforming synthetic football events into explainable tactical insights, with evidence validation, an interactive dashboard, and personalized Fan/Analyst experiences in English and French.

## Current milestone: demo scenario verification (Task 8)

Implemented:
- A responsive React/Vite match dashboard and FastAPI foundation.
- Version 1 Pydantic event, fixture, request, response, evidence, trace, and error models.
- Read-only demo match/event endpoints and a validated synthetic eight-event fixture.
- OpenAPI and JSON Schema exports, generated TypeScript types, and contract tests.
- Eight illustrative processing responses covering both audience modes, both languages, failed passes, regains, and missing annotations.
- A working three-stage mock workflow: Match Intelligence, Tactical Explainer, and Trust & Personalization.
- Runtime geometry, sequence-prefix statistics, evidence checks, English/French Fan/Analyst templates, and measured stage traces.
- Visible mock fallback behavior and rejection of conflicting structured claims.
- An SVG pitch with source-coordinate overlays, sequence trails, event selection, timed replay, seeking, and speed controls.
- English/French Fan/Analyst presentation, evidence and trust tabs, sequence statistics, filters, and expandable illustrative agent outputs.
- Thirty-two typed, reproducible sample views exported from the canonical mock workflow. Sample mode works without the backend.
- An Azure OpenAI v1 Responses adapter with strict structured candidates, local trust checks, bounded connection/read timeouts, and visible mock fallback.
- An offline configuration checker and an explicit one-request live preflight that never substitutes a mock result.
- API mode that loads match/events from FastAPI and posts selections and preferences for runtime analysis.
- Schema and source-consistency checks in the browser, loading/error states, explicit retry, cancellation, session caching, and replay that waits for processing.
- Provider provenance, measured runtime traces, visible backend fallback warnings, and a separate offline sample mode.
- A connected React/FastAPI demo rehearsal covering personalization, evidence, sequence totals, explicit samples, actual configuration fallback, and API outage/recovery.
- A single automated verification command and a team acceptance checklist for the final demo.

`POST /events/process` returns **200** for a valid known event, with `result_source: "runtime"`. The default `LLM_PROVIDER=mock` runs entirely locally. A configured `azure` provider calls one deployment for a structured tactical candidate; geometry, evidence, trust checks, and narrative templates remain local. The static Task 3 examples remain marked `result_source: "example"` and are never loaded as runtime results.

Azure access is **not established by installing this code or by `/health`**. Complete the [Azure setup and live verification](docs/azure-setup.md) in your own subscription. No resource or deployment is created automatically.

The fixture is **pending Member 2 review**. Geometry and evidence links are checked automatically; tactical interpretations and authored annotations still need team validation.

The dashboard starts in **API mode**. It loads the canonical match and events from FastAPI, then processes the selected event and preferences. Results are labelled `AZURE · RUNTIME`, `MOCK · RUNTIME`, or `MOCK FALLBACK`. **Samples** is an explicit separate mode, labelled `SAMPLE DATA`; it works without FastAPI and makes no processing requests. API failures show an error with retry and a deliberate switch to samples. The optional **API connection** link opens a separate health check.

## Prerequisites

- Git.
- Node.js 24.12.0 and npm 11 (the Node version is recorded in `.nvmrc`).
- Python 3.12 with `venv` support.

If you use nvm, run `nvm install` and `nvm use` in the repository root. Use a dedicated Python virtual environment even if Conda is installed.

## Clone

```bash
git clone https://github.com/LeBossKing/MatchPulse-AI.git
cd MatchPulse-AI
```

## Start the backend (terminal 1)

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

For subsequent runs, activate `.venv` and run the final command again. Only copy the environment example on initial setup; preserve later local configuration.

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and use `Copy-Item .env.example .env`.

- Health: <http://127.0.0.1:8000/health>
- Interactive API docs: <http://127.0.0.1:8000/docs>

## Start the frontend (terminal 2)

From the repository root:

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Open <http://localhost:5173> with FastAPI running. The dashboard loads the main synthetic event, `evt-064` at 63:24, in Analyst/English mode. After processing, expect length `44.28`, progression `+40`, and one source-annotated line bypassed. With `LLM_PROVIDER=azure` and a working deployment, the badge shows `AZURE · RUNTIME`. With the default mock provider, it shows `MOCK · RUNTIME`.

If FastAPI is stopped, click **Use sample data** to open the offline examples. To check the backend separately, click **API connection** in the sidebar. With FastAPI running, that panel should show **Backend connected**, API version `0.4.0`, and environment `development`.

The dev server uses port 5173 and fails clearly if it is occupied. This keeps it consistent with the backend's allowed origins.

## Configuration

| File | Variable | Purpose |
| --- | --- | --- |
| `backend/.env` | `APP_ENV` | `development`, `test`, or `production`; defaults to `development`. |
| `backend/.env` | `FRONTEND_ORIGIN` | Additional allowed browser origin; defaults to `http://localhost:5173`. |
| `backend/.env` | `LLM_PROVIDER` | `mock` by default; set `azure` after the live preflight succeeds. Missing/invalid Azure settings produce a visible fallback. |
| `backend/.env` | `AZURE_OPENAI_ENDPOINT` | Backend-only HTTPS resource endpoint on `openai.azure.com` or `services.ai.azure.com`, optionally ending in `/openai/v1/`. |
| `backend/.env` | `AZURE_OPENAI_DEPLOYMENT` | Your actual model deployment name, not the model catalog ID. |
| `backend/.env` | `AZURE_OPENAI_API_KEY` | Backend-only resource key. Never put it in a `VITE_*` variable. |
| `backend/.env` | `AZURE_OPENAI_TIMEOUT_SECONDS` | HTTP timeout per operation, 2–60 seconds; default 15. Connection timeout is capped at 5 seconds. |
| `backend/.env` | `AZURE_OPENAI_MAX_OUTPUT_TOKENS` | Output token limit, 256–8192; default 2048. |
| `frontend/.env` | `VITE_API_BASE_URL` | Public API URL; defaults to `http://127.0.0.1:8000`. |

Restart the relevant dev server after changing its environment file. Local environment files and virtual environments are ignored by Git. Configuration examples remain tracked. `VITE_*` values are exposed to the browser; keep all credentials in backend configuration.

From `backend/`, run `python scripts/check_azure.py` to check configuration without network access. Once configured, `python scripts/check_azure.py --live` makes one token-consuming Azure request and applies the same local trust checks as the API. Only `status: live_verified` completes that deployment check; an HTTP 200 from the normal API can be a labelled mock fallback.

## Verify the application

For the complete Task 8 checks, install `backend/requirements-dev.txt` into `backend/.venv` and run `npm ci` in `frontend/`. Then, from the repository root:

```bash
python scripts/verify_demo.py
```

This runs backend and frontend tests, real HTTP scenario tests, contract/sample checks, lint, and the production build without Azure model calls. See [scenario testing and the manual demo checklist](docs/testing.md) for final acceptance.

```bash
# In frontend/
npm run test
npm run lint
npm run build
```

```bash
# With the backend running
curl http://127.0.0.1:8000/health
```

In API mode, stop FastAPI and choose an uncached event/preference combination or click **Run analysis again**. The analysis shows an error and never relabels a stored example as runtime. Restart FastAPI and click **Retry**, or explicitly select **Samples** for offline use. Session-cached results can still be viewed and are labelled as cached.

Select different timeline events, try Fan/French, inspect the evidence and trust tabs, and use replay, pause, speed, and rewind. API mode waits for each result before advancing replay. Revisiting the same event/audience/language uses a five-minute browser-session cache; **Run analysis again** forces a fresh request. `evt-065` preserves the failed attempt; `evt-067` shows unknown annotations and limited context. See [dashboard acceptance checks](docs/dashboard.md).

For `npm run preview`, set `FRONTEND_ORIGIN=http://localhost:4173` in `backend/.env` and restart the backend, since Vite preview uses a different origin.

## Check and regenerate the contract

From `backend/`, with the virtual environment activated:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/export_contract.py --check
```

After changing backend models, regenerate the checked-in API artifacts, including the browser JSON Schema bundle:

```bash
# In backend/
python scripts/export_contract.py
```

```bash
# In frontend/
npm run generate:api
npm run lint
npm run build
```

The type generator runs as a pinned isolated CLI because its TypeScript 5 peer dependency differs from the app's TypeScript 6 compiler. Normal app startup uses the checked-in types; the first generator run needs network access. Commit model changes, schema exports, and generated TypeScript together.

Try the read endpoints with the backend running:

```bash
curl http://127.0.0.1:8000/matches/demo
curl http://127.0.0.1:8000/matches/demo/events
```

See [the contract](docs/api-contract.md) for processing requests, response examples, validation rules, and current endpoint status.

## Test event processing

Keep `LLM_PROVIDER=mock` in `backend/.env`, start the backend, and send:

```bash
curl -X POST http://127.0.0.1:8000/events/process \
  -H 'Content-Type: application/json' \
  -d '{"match_id":"match-demo-01","event_id":"evt-064","audience":"analyst","language":"en"}'
```

Expected: HTTP 200, pass length `44.28`, forward progression `40`, four events in the prefix, three actual stage traces, and a grounded explanation. `validation.status: validated` means the structured claims passed the mock rules; the fixture remains `pending_review` until Member 2 approves it.

Change `audience` to `fan`, `language` to `fr`, or `event_id` to `evt-067` to inspect the missing-annotation case (`validation.status: limited`). Replaying or rewinding does not double-count events.

Import [the Postman collection](docs/postman/MatchPulse-AI.postman_collection.json) to run the success, personalization, missing-data, failed-pass, regain, 404, and 422 checks. Its `base_url` variable defaults to `http://127.0.0.1:8000`.

See [workflow design and acceptance checks](docs/mock-workflow.md) for trust rules, importance thresholds, and fallback behavior. See [Azure setup](docs/azure-setup.md) for deployment verification and troubleshooting. See [runtime integration](docs/integration.md) for request behavior and connected acceptance checks.

## Regenerate dashboard samples

The checked-in TypeScript corpus contains eight events in both languages and audience modes. It is generated from the mock workflow, then explicitly marked as illustrative with zero placeholder durations. It is never presented as a live run.

```bash
# In backend/, with the virtual environment activated
python scripts/export_dashboard_samples.py --check
python scripts/export_dashboard_samples.py
```

Use `--check` to detect drift; run the second command only when updating samples. Then run frontend lint/build and commit the generated file with the source changes. App startup needs no Python process or generator command.

## Project layout

- `backend/app/api/`: HTTP routes.
- `backend/app/models/`: Pydantic request/response models.
- `backend/app/agents/`: stage contracts, intelligence, candidate rules, and trust/personalization.
- `backend/app/services/`: pure statistics, narrative templates, provider boundary, and orchestrator.
- `backend/data/`: the synthetic fixture, example responses, and review notes.
- `backend/tests/`: event, API, fixture, evidence, and example consistency tests.
- `frontend/src/api/`: typed HTTP client.
- `frontend/src/components/`: interface components.
- `frontend/src/hooks/`: connection checks and timed sequence replay.
- `frontend/src/types/`: generated API types and convenient named aliases.
- `frontend/src/data/`: typed sample views aligned with the event/API contract.
- `frontend/src/lib/`: interface translations and formatting helpers.
- `docs/`: architecture, API contract status, and demo plan.

## Team workflow

- **Member 1 - Full-Stack Developer & AI Engineer:** implementation, integration, Azure configuration, and technical fixes.
- **Member 2 - Data, Research & AI Validation:** synthetic data, evidence requirements, tactical validation, and test cases.
- **Member 3 - Product, Testing & Presentation:** requirements, acceptance testing, bug reports, documentation content, pitch, and demo video.

Create one branch per feature and use small pull requests. Include the reason for the change and the checks performed. Agree on the JSON contract with the team before developing the match UI and agent workflow against it.

See [runtime integration](docs/integration.md), [dashboard design and acceptance](docs/dashboard.md), [architecture](docs/architecture.md), [API contract](docs/api-contract.md), and [demo plan](docs/demo-script.md).

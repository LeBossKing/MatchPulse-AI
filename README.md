# MatchPulse AI

Agentic AI prototype transforming synthetic football events into explainable tactical insights, with evidence validation, an interactive dashboard, and personalized Fan/Analyst experiences in English and French.

## Current milestone: backend mock workflow (Task 4)

Implemented:
- The React/Vite connection screen and FastAPI foundation.
- Version 1 Pydantic event, fixture, request, response, evidence, trace, and error models.
- Read-only demo match/event endpoints and a validated synthetic eight-event fixture.
- OpenAPI and JSON Schema exports, generated TypeScript types, and contract tests.
- Eight illustrative processing responses covering both audience modes, both languages, failed passes, regains, and missing annotations.
- A working three-stage mock workflow: Match Intelligence, Tactical Explainer, and Trust & Personalization.
- Runtime geometry, sequence-prefix statistics, evidence checks, English/French Fan/Analyst templates, and measured stage traces.
- Visible mock fallback behavior and rejection of conflicting structured claims.

`POST /events/process` now returns **200** for a valid known event, with `result_source: "runtime"`. Processing uses deterministic Python rules and templates; no model or Azure request is made. The static Task 3 examples remain marked `result_source: "example"` and are never loaded as runtime results.

The fixture is **pending Member 2 review**. Geometry and evidence links are checked automatically; tactical interpretations and authored annotations still need team validation.

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

Open <http://localhost:5173>. The page should show **Backend connected**, API version `0.3.0`, and environment `development`.

The dev server uses port 5173 and fails clearly if it is occupied. This keeps it consistent with the backend's allowed origins.

## Configuration

| File | Variable | Purpose |
| --- | --- | --- |
| `backend/.env` | `APP_ENV` | `development`, `test`, or `production`; defaults to `development`. |
| `backend/.env` | `FRONTEND_ORIGIN` | Additional allowed browser origin; defaults to `http://localhost:5173`. |
| `backend/.env` | `LLM_PROVIDER` | Defaults to `mock`. Selecting `azure` currently produces a visible mock fallback; Azure is not implemented yet. |
| `backend/.env` | `AZURE_OPENAI_ENDPOINT` | Future backend-only Azure endpoint. |
| `backend/.env` | `AZURE_OPENAI_DEPLOYMENT` | Future backend-only Azure model deployment name. |
| `backend/.env` | `AZURE_OPENAI_API_KEY` | Future backend-only Azure credential. |
| `frontend/.env` | `VITE_API_BASE_URL` | Public API URL; defaults to `http://127.0.0.1:8000`. |

Restart the relevant dev server after changing its environment file. Local environment files and virtual environments are ignored by Git. Configuration examples remain tracked. `VITE_*` values are exposed to the browser; keep all credentials in backend configuration.

## Verify the foundation

```bash
# In frontend/
npm run lint
npm run build
```

```bash
# With the backend running
curl http://127.0.0.1:8000/health
```

Also stop the backend and click **Check connection**: the page must show **Backend unavailable**. Restart FastAPI and retry to recover. The frontend remains the foundation connection screen; the match dashboard follows in Task 5.

For `npm run preview`, set `FRONTEND_ORIGIN=http://localhost:4173` in `backend/.env` and restart the backend, since Vite preview uses a different origin.

## Check and regenerate the contract

From `backend/`, with the virtual environment activated:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/export_contract.py --check
```

After changing backend models, regenerate the checked-in API artifacts:

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

See [workflow design and acceptance checks](docs/mock-workflow.md) for trust rules, importance thresholds, fallback behavior, and remaining Azure/frontend work.

## Project layout

- `backend/app/api/`: HTTP routes.
- `backend/app/models/`: Pydantic request/response models.
- `backend/app/agents/`: stage contracts, intelligence, candidate rules, and trust/personalization.
- `backend/app/services/`: pure statistics, narrative templates, provider boundary, and orchestrator.
- `backend/data/`: the synthetic fixture, example responses, and review notes.
- `backend/tests/`: event, API, fixture, evidence, and example consistency tests.
- `frontend/src/api/`: typed HTTP client.
- `frontend/src/components/`: interface components.
- `frontend/src/hooks/`: connection and application hooks.
- `frontend/src/types/`: generated API types and convenient named aliases.
- `frontend/src/data/`: future sample data aligned with the agreed contract.
- `docs/`: architecture, API contract status, and demo plan.

## Team workflow

- **Member 1 - Full-Stack Developer & AI Engineer:** implementation, integration, Azure configuration, and technical fixes.
- **Member 2 - Data, Research & AI Validation:** synthetic data, evidence requirements, tactical validation, and test cases.
- **Member 3 - Product, Testing & Presentation:** requirements, acceptance testing, bug reports, documentation content, pitch, and demo video.

Create one branch per feature and use small pull requests. Include the reason for the change and the checks performed. Agree on the JSON contract with the team before developing the match UI and agent workflow against it.

See [architecture](docs/architecture.md), [API contract](docs/api-contract.md), and [demo plan](docs/demo-script.md).

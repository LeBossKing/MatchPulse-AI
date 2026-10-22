# MatchPulse AI

Agentic AI prototype transforming synthetic football events into explainable tactical insights, with evidence validation, an interactive dashboard, and personalized Fan/Analyst experiences in English and French.

## Current milestone: project foundation

Implemented:
- React + TypeScript + Vite frontend with a responsive connection screen.
- FastAPI backend with a typed `GET /health` response and interactive API documentation.
- Real frontend-to-backend connection checking, a five-second timeout, retry, and error states.
- Backend-only environment configuration, safe examples, and local CORS settings.

Next: agree on the event/API contract, implement the mock agent workflow, then build the match dashboard. Match analysis, AI agents, and Azure calls are not implemented in this foundation. A successful health check confirms API connectivity only.

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

Open <http://localhost:5173>. The page should show **Backend connected**, API version `0.1.0`, and environment `development`.

The dev server uses port 5173 and fails clearly if it is occupied. This keeps it consistent with the backend's allowed origins.

## Configuration

| File | Variable | Purpose |
| --- | --- | --- |
| `backend/.env` | `APP_ENV` | `development`, `test`, or `production`; defaults to `development`. |
| `backend/.env` | `FRONTEND_ORIGIN` | Additional allowed browser origin; defaults to `http://localhost:5173`. |
| `backend/.env` | `LLM_PROVIDER` | Provider selection for the later AI implementation; defaults to `mock`. |
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

Also stop the backend and click **Check connection**: the page must show **Backend unavailable**. Restart FastAPI and retry to recover. Agent/statistics tests will be added alongside those implementations in later tasks.

For `npm run preview`, set `FRONTEND_ORIGIN=http://localhost:4173` in `backend/.env` and restart the backend, since Vite preview uses a different origin.

## Project layout

- `backend/app/api/`: HTTP routes.
- `backend/app/models/`: Pydantic request/response models.
- `backend/app/agents/`: reserved for the three agent roles and orchestrator.
- `backend/app/services/`: reserved for deterministic statistics and model providers.
- `backend/data/`: validated synthetic match fixtures, supplied in Task 3.
- `backend/tests/`: tests added with the event processing implementation.
- `frontend/src/api/`: typed HTTP client.
- `frontend/src/components/`: interface components.
- `frontend/src/hooks/`: connection and application hooks.
- `frontend/src/types/`: TypeScript API types.
- `frontend/src/data/`: future sample data aligned with the agreed contract.
- `docs/`: architecture, API contract status, and demo plan.

## Team workflow

- **Member 1 - Full-Stack Developer & AI Engineer:** implementation, integration, Azure configuration, and technical fixes.
- **Member 2 - Data, Research & AI Validation:** synthetic data, evidence requirements, tactical validation, and test cases.
- **Member 3 - Product, Testing & Presentation:** requirements, acceptance testing, bug reports, documentation content, pitch, and demo video.

Create one branch per feature and use small pull requests. Include the reason for the change and the checks performed. Agree on the JSON contract with the team before developing the match UI and agent workflow against it.

See [architecture](docs/architecture.md), [API contract](docs/api-contract.md), and [demo plan](docs/demo-script.md).

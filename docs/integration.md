# Task 7: runtime dashboard integration

The dashboard now uses FastAPI by default. It supports an explicit offline sample mode and preserves the same synthetic source, event schema, evidence rules, and audience/language options.

## Local setup

Keep the verified endpoint, deployment name, and key in your ignored `backend/.env`. Set `LLM_PROVIDER=azure` for the Azure demo, or `mock` for offline backend development. The frontend receives no Azure credentials.

Terminal 1, from the repository root:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. `VITE_API_BASE_URL` defaults to `http://127.0.0.1:8000`. If you change this public URL, restart Vite. FastAPI permits the documented localhost/127.0.0.1 development origins; for preview or another frontend origin, set `FRONTEND_ORIGIN` in the backend and restart it. A deployed frontend needs a reachable backend URL, configured CORS, and HTTPS as applicable; a production browser cannot reach a developer's localhost service.

## Request flow

| Trigger | Request / behavior |
| --- | --- |
| Open API workspace | Parallel `GET /matches/demo` and `GET /matches/demo/events`; validate both before rendering the match. |
| Select an uncached event or preferences | `POST /events/process` with only match/event IDs, audience, and language. |
| Rapid navigation | Coalesce changes for 200 ms before POST; abort obsolete browser requests and ignore late replies. |
| Revisit an identical selection | Reuse a labelled session entry if younger than five minutes. |
| Run analysis again / Retry | Bypass the current cache entry and send one explicit new request. |
| Select Samples | Load the static example chunk and make no match/processing requests. |
| Open API connection panel | Separate `/health` request. Health does not verify model access. |

Read calls have a 10-second deadline; processing has a 75-second deadline. There are no automatic retries. Browser abort prevents stale UI updates, but cannot guarantee cancellation of work already running on the backend or Azure. Processing still uses the backend's bounded provider timeout and visible mock fallback.

The cache is request-local to a mounted browser workspace, not a server cache or persistent store. It contains at most 64 entries and is cleared by mode switching or page reload. Runtime results keep their original traces; cached does not mean agents are executing again. A fallback can also be cached; use **Run analysis again** after fixing the provider to request Azure again.

## Validation and UI states

`export_contract.py` produces the read-response schemas and `frontend/src/api/generated-schemas.json` alongside existing exports. Ajv validates shapes without coercion, defaults, or field removal. Further source checks bind the response to the requested match/event/preferences and the canonical sequence: IDs, event values, geometry, overlay, prefix totals, evidence values/references, trace roles/order, and actual-provider consistency.

Backend Pydantic validation and Trust & Personalization remain authoritative. Browser validation is an additional guard against stale, mismatched, or malformed data; it is not an independent tactical fact checker.

Pending requests show a loading state and hide the previous analysis. Errors show safe local text with HTTP/error codes where available, explicit retry, and the sample-mode choice. Raw upstream error bodies are not displayed. Rejected insights remain withheld; limited context and fallback are visible outcomes. API failures never cause stored examples to appear under runtime provenance.

Runtime stage cards show the backend's statuses, summaries, durations, and raw trace JSON. Durations include provider waiting time and exclude browser/network overhead. There is no invented stage-by-stage progress while the REST request is pending. Sample cards retain illustrative labels and no timing claims.

## Verification

From `frontend/`:

```bash
npm run test
npm run lint
npm run build
```

The normal suite covers payload validation, malformed/source-mismatched responses, empty or inconsistent fixtures, transport errors/timeouts/cancellation, stale replies, StrictMode duplicate-POST prevention, cache keys/expiry/refresh, explicit retry, API/sample separation, provider badges, warnings, and replay backpressure. Its Azure/fallback responses are explicit test doubles.

For real local HTTP integration, install backend dependencies into `backend/.venv` first, then run from `frontend/`:

```bash
MATCHPULSE_RUN_API_TESTS=1 npm run test
```

This opt-in test launches FastAPI on a temporary local port in **mock mode**, validates all 32 event/audience/language variants through the actual TypeScript HTTP client, verifies POST CORS preflight, and checks structured 404 behavior. It overrides Azure settings to prevent model calls. The normal suite skips these two tests so frontend-only development needs no Python installation.

From `backend/`:

```bash
python -m pytest -q
python scripts/export_contract.py --check
python scripts/export_dashboard_samples.py --check
```

The browser layout check covers explicit offline/error states and responsive sample mode at desktop and 320/390/768 px widths. Actual Azure execution must be checked from the configured developer machine; the isolated preview browser cannot access that machine's localhost backend.

## Live Azure acceptance

1. Verify `python scripts/check_azure.py --live` returns `live_verified` on the configured machine.
2. Set `LLM_PROVIDER=azure`, restart FastAPI, and open the dashboard in API mode.
3. Confirm `AZURE · RUNTIME`, `evt-064`, 44.28 / +40 / 1, and three measured stage traces. Inspect the tactical trace for `actual_provider: azure` and `fallback_reason: null`.
4. Try Fan/French, missing annotations (`evt-067`), and a regain. Geometry and prefix statistics must retain their source meaning.
5. Revisit the main selection to see the cache label, then click **Run analysis again** for another execution.
6. Stop FastAPI and rerun to verify the explicit API error; select Samples deliberately to continue offline. Restart FastAPI and return to API mode.

Source annotations remain pending Member 2 review until actually approved. Task 8 covers the final team scenario and remaining bugs; Task 9 prepares the pitch, documentation, and recorded demonstration.

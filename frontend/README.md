# MatchPulse AI frontend

React, TypeScript, and Vite dashboard for the synthetic Atlas FC / Harbor FC sequence. Task 7 connects it to FastAPI while retaining an explicit offline sample mode.

## Run

Start FastAPI in a separate terminal. From `frontend/`:

```bash
npm ci
npm run dev
```

Open <http://localhost:5173>. The default API base URL is `http://127.0.0.1:8000`; set `VITE_API_BASE_URL` in your local `frontend/.env` if needed and restart Vite. Preserve an existing environment file. All `VITE_*` values are public browser configuration; Azure credentials belong only in `backend/.env`.

## API mode

The default mode loads `GET /matches/demo` and `GET /matches/demo/events`, then posts the selected identifiers and audience/language to `/events/process`. Backend provider configuration decides whether analysis uses Azure, deterministic mock rules, or a labelled mock fallback.

- Loading and errors hide the prior selection's analysis.
- Rapid selections are coalesced for 200 ms; obsolete browser requests are aborted and late replies are ignored.
- Revisited event/audience/language selections reuse a browser-session cache for up to five minutes. Its badge identifies cached results and original timings. **Run analysis again** bypasses that entry.
- Replay waits for the current analysis before advancing. Errors pause playback; retry is explicit.
- Actual runtime traces show stage status, measured duration, summary, and inspectable JSON. Processing warnings appear under Trust notes.
- API failures never switch to examples automatically. Choose **Samples** or **Use sample data** deliberately for offline examples.

The browser validates payloads using generated JSON Schemas plus checks for canonical event/preference identity, metrics, evidence, overlays, prefix statistics, trace order, and provider provenance. Backend Pydantic and trust validation remain authoritative.

## Sample mode

**Samples** loads the checked-in 32-view corpus as a separate JavaScript chunk. It makes no match/processing API calls, displays `SAMPLE DATA`, and uses illustrative trace outputs with no runtime timing claims. Opening the optional API connection panel separately makes a health request.

## Checks

```bash
npm run test
npm run lint
npm run build
```

The normal suite uses simulated transports and needs no running Python server or Azure access. An optional test starts real FastAPI in mock mode and exercises all 32 variants over HTTP. First install backend dependencies into `backend/.venv`, then run from `frontend/`:

```bash
MATCHPULSE_RUN_API_TESTS=1 npm run test
```

The optional test never uses Azure credentials. On Windows PowerShell, set `$env:MATCHPULSE_RUN_API_TESTS="1"` before `npm run test`, then remove that environment variable afterward.

## Contract generation

From `backend/`, activate the virtual environment and run:

```bash
python scripts/export_contract.py
python scripts/export_dashboard_samples.py --check
```

Then from `frontend/`:

```bash
npm run generate:api
npm run test
npm run lint
npm run build
```

Commit backend models, exported schemas, `src/api/generated-schemas.json`, and generated TypeScript together. The browser schema bundle is produced by the backend exporter; do not edit it manually. Normal startup uses committed artifacts and needs no generation step.

See [runtime integration](../docs/integration.md), [dashboard behavior](../docs/dashboard.md), and [Azure setup](../docs/azure-setup.md).

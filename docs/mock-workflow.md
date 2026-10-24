# Task 4: deterministic mock workflow

The backend executes three stages for a canonical match/event selector and returns HTTP 200. With `LLM_PROVIDER=mock`, no Azure credentials, external API, or response-example files are used. Task 6 adds an optional Azure candidate provider; the calculations, trust rules, and templates below apply to both providers.

## Stage boundaries

| Stage | Input | Output |
| --- | --- | --- |
| Match Intelligence | Validated fixture and selected index | Copied event, geometry, sequence-prefix statistics, evidence, overlay |
| Tactical Explainer | An isolated copy of the intelligence result | Structured claims, interpretation category, heuristic importance |
| Trust & Personalization | Original trusted facts, structured candidate, audience/language | Accepted template-rendered insight, or null insight with rejection reasons |

The orchestrator is `backend/app/services/workflow.py`; the three stage modules live in `backend/app/agents/`. Each trace has measured elapsed time and inspectable intermediate output. Trace summaries and internal audit messages use English; the insight, limitations, and user-facing warnings support English/French.

## Calculations

- Pass length: Euclidean distance between recorded start/end coordinates, rounded to two decimals, in **normalized pitch units**, not metres.
- Forward progression: `end.x - start.x` for left-to-right attacks, the inverse for right-to-left. Negative means backward; zero means no forward progression. For failed passes this is endpoint displacement, not a completed gain.
- Interceptions/recoveries have point overlays and null pass metrics.
- Team totals describe only the fixture prefix ending at the selected event. Accuracy is completed/attempted times 100, rounded to two decimals; null before any attempts.
- The fixture, initial GET statistics, and prior results are never incrementally mutated. Replay, rewind, and concurrent selections are independent.

## Candidate and trust rules

Providers return a typed `TacticalCandidate`: event ID, exact primitive evidence claims, interpretation category, and importance. Free-form provider narrative is not accepted. The trust stage requires the complete canonical evidence set, unique claim IDs, correct source/field/value mappings, the selected event ID, and the expected interpretation/importance rules. Boolean values cannot masquerade as numeric claims. Unsupported, missing, duplicate, or conflicting claims produce `validation.status: rejected`, `insight: null`, and an explanatory warning. The trust check still has trace status `completed` because the check ran successfully.

Approved text is rendered only from the trusted canonical event, calculated metrics, fixture roster, and fixed English/French templates. This prevents unverified provider prose from entering the insight; it is not a general natural-language fact checker. Interpretation is cautious and separate from recorded facts.

Interpretation categories are completed forward progression (`advance`), completed non-forward circulation (`retain`), unsuccessful attempt (`attempt_failed`), and regain (`regain`). These categories describe the selected event, without forecasting a goal or inventing defender positions.

Importance is an explicit demo heuristic, not a calibrated model score:

| Condition | Importance |
| --- | --- |
| Completed pass, progression at least 20, at least one annotated line bypassed | high |
| Other completed pass with progression at least 15 | medium |
| Interception or recovery | medium |
| Other passes, including failed attempts | low |

Missing pressure or a missing pass line-break annotation produces `limited` validation while preserving known facts. Explicit zero lines is known information. Other accepted candidates are `validated`; this means internal rule consistency, not external verification or team approval. The fixture remains `pending_review` until Member 2 actually reviews it. Synthetic-data, coordinate-unit, sequence-scope, and unavailable tracking limitations remain visible.

## Provider failures and Azure configuration

`LLM_PROVIDER=azure` selects the Azure Responses adapter when the backend endpoint, deployment, and resource key are configured. A successful candidate reports `provider: azure` and `actual_provider: azure`. Only this stage calls the model; its claims still go through local trust checks and controlled narrative rendering.

Missing or invalid settings select the deterministic fallback with `provider: fallback`, `requested_provider: azure`, `actual_provider: mock`, and `fallback_reason: azure_configuration`. Its warning states that no Azure request was sent.

Expected upstream failures or malformed candidate structures also trigger a mock fallback and record failed/completed attempts. Azure failures have safe reason codes such as `azure_auth`, `azure_rate_limit`, or `azure_invalid_response`; other provider failures use `provider_error`. These warnings acknowledge the Azure failure rather than claiming no model was called. Exception text and credentials are excluded from public diagnostics. A structurally valid conflicting candidate goes to trust and is rejected; it does not trigger a silent rewrite. If both provider and fallback fail, the route returns the common 500 envelope with `error.code: processing_failed`.

Azure connection/read timeouts are bounded and requests are not automatically retried. See [Azure setup](azure-setup.md) for configuration, actual-access verification without fallback, and diagnostic codes. A normal processing response with HTTP 200 alone does not establish Azure access.

## Acceptance checks

Start the backend, import `docs/postman/MatchPulse-AI.postman_collection.json`, and run the collection. Alternatively use Swagger at `http://127.0.0.1:8000/docs`.

1. Main event `evt-064`: HTTP 200, `runtime`, `mock`, length 44.28, progression 40, prefix count 4, Atlas 4/4 passes, three ordered completed traces.
2. Fan/French: explanation changes; event, metrics, evidence, and prefix counts remain identical.
3. `evt-065`: unsuccessful attempt preserved, low importance, no claim of a completed gain.
4. `evt-066` and `evt-068`: point markers and null pass metrics.
5. `evt-067`: right-to-left progression +16, null tactical annotations, `limited` validation, no fabricated line-break evidence.
6. Process the final event, rewind to the first, and select the main event twice: prefix totals stay stable. `GET /matches/demo` remains zeroed.
7. Unknown event: 404 `event_not_found`. Unsupported audience: 422 `invalid_request`.

The pytest suite additionally injects conflicting claims, provider mutation, malformed structures, upstream failures, unrecoverable failures, and parallel selections. Run from `backend/`:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/export_contract.py --check
```

Testing follows the official [FastAPI TestClient guidance](https://fastapi.tiangolo.com/tutorial/testing/). Cross-field response validation follows the [Pydantic model validator guidance](https://docs.pydantic.dev/latest/concepts/validators/).

## Dashboard and next milestone

Task 5 implements the React dashboard using clearly labelled sample data; see [dashboard documentation](dashboard.md). Task 6 provides the Azure adapter and environment checks; the subscription owner must complete the live verification. Frontend/backend processing integration is Task 7. Member 2 reviews the data and tactical interpretation; Member 3 can use the collection and acceptance checks to report issues.

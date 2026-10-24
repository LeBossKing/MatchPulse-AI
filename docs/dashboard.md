# Match dashboard

The responsive React dashboard has two explicit modes. It starts in **API mode**, reading canonical match/events from FastAPI and processing selections at runtime. **Samples** is the offline corpus from Task 5. Both modes retain synthetic-data and team-review provenance.

## Controls

| Control | Behavior |
| --- | --- |
| API mode / Samples | Switches the data source and resets the workspace/cache. API errors never switch sources automatically. |
| Event timeline, previous/next, seek, key event, reset | Select a canonical event; manual selection pauses replay. |
| Replay and 1×/2×/4× speed | Use source timestamp gaps divided by speed. API mode also waits for the current result. Stops at the final event; replaying from the end starts at the first event. |
| Audience and language | Request a runtime result or select the matching sample. Facts and canonical prefix counters remain unchanged. |
| Previous actions | Shows source-coordinate trails before the selected event. |
| Search and event-type filter | Affect the visible timeline only; selection and prefix statistics remain canonical. |
| Insight / Evidence / Trust notes | Explain the accepted result, expose source facts, and show validation, warnings, limitations, and review status. Tabs support arrow/Home/End keyboard navigation. |
| Run analysis again | API mode only. Forces a new processing request for this selection. |
| Agent output disclosures | Runtime: actual status, duration, summary, and JSON. Samples: illustrative output without timing claims. |
| API connection | Optional separate health check. It does not establish Azure access. |

## Runtime state and provenance

The main provider badge is `AZURE · RUNTIME`, `MOCK · RUNTIME`, or `MOCK FALLBACK`. The result bar distinguishes a new API result from a cached result. Before a response arrives, it says API workspace and processing; previous analysis, evidence, counters, and traces are hidden. Source pitch coordinates and authored annotations can still be inspected while waiting.

An API error shows a safe message, HTTP/code information where available, Retry, and an explicit sample-mode action. Backend fallback results retain their own warning and mock provenance; they remain runtime executions. A rejected candidate keeps its evidence and trace while withholding the insight. Unknown annotations stay unknown; point events retain null pass metrics.

The per-workspace cache holds up to 64 event/preference results and reuses entries younger than five minutes. It retains the original provider and measured times. Reloading or switching modes clears it. There are no automatic retries or background processing prefetches.

## Synthetic pitch semantics

Coordinates are normalized to 0–100 and are not metres. The SVG uses source points only, including failed pass endpoints. Regains use point markers. Trails show recorded event locations, not defender formations or inferred player tracking. Pressure and lines bypassed are authored annotations. Statistics describe the selected sequence prefix, never the full match.

## Offline corpus

`frontend/src/data/dashboard-samples.ts` contains eight events × two languages × two audiences. `backend/scripts/export_dashboard_samples.py` runs the mock workflow at authoring time, revalidates each response, sets `result_source: example`, uses zero placeholder durations, and records sample provenance. The corpus is lazy-loaded only when Samples is selected.

From `backend/`, with the virtual environment active:

```bash
python scripts/export_dashboard_samples.py --check
python scripts/export_dashboard_samples.py
```

Use the second command after deliberately changing the fixture or narrative. Commit the export alongside source changes and run frontend checks. API mode does not use these examples as processing results.

## Acceptance checks

1. Start both apps. API mode opens `evt-064` and eventually displays 44.28 normalized units, progression +40, one annotated line, and Atlas 4/4 prefix passes.
2. Check the provider badge, new/cached result label, measured trace durations, and warning notes. Azure appears only when the backend actually reports Azure.
3. Change Fan/Analyst and EN/FR. The selected event and factual metrics remain stable while presentation changes.
4. Select `evt-065`: preserve the failed pass and cautious endpoint displacement. Select `evt-066` or `evt-068`: show a point and null pass metrics.
5. Select `evt-067`: right-to-left progression +16, unknown annotations, limited context, and no invented line-break evidence.
6. Select rapidly while processing. Only the current selection's response may appear. Revisit a selection to show a cached result; rerun to obtain a new execution.
7. Replay in API mode. The selected event stays in place while its analysis is pending. Manual seeking pauses; final playback stops.
8. Stop FastAPI and rerun an analysis. Show the error, then deliberately switch to Samples. Restart FastAPI and return to API mode to recover.
9. Test desktop and mobile widths, keyboard tabs, filters, and empty-filter recovery. Offline sample mode must retain its labels and illustrative traces.

The API transport and source checks are tested separately from the backend's authoritative trust logic. See [integration details](integration.md) for HTTP, CORS, and live Azure verification.

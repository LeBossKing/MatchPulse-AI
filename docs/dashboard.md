# Task 5: React dashboard with sample data

The dashboard replaces the foundation landing screen while preserving the optional backend health check. Start it from `frontend/` with `npm ci` and `npm run dev`. FastAPI and Azure are not required for sample mode.

## Interaction and data

- Initial view: the main pass `evt-064`, Analyst audience, English, replay paused at 63:24. Switching audience/language selects a corresponding preloaded view; source facts and prefix totals remain identical.
- Pitch: canonical start/end coordinates only. Passes use arrows; unsuccessful attempts are dashed with a cross at the recorded endpoint. Interceptions/recoveries use point markers and null pass metrics. No defender locations or formations are fabricated. The optional previous-action trails stop before the selected event, so future passes never appear early.
- Metrics: normalized pass length, signed forward progression, and source-annotated line breaks. Unknown annotations show `?`/Unknown; zero is shown as zero. Point events show Not applicable. Failed-pass displacement is not described as a completed gain.
- Replay: source timestamp gaps divided by 1×, 2×, or 4×. Play from the final event restarts at the first. Playback stops automatically at the final event. Previous/next, timeline selection, slider seeking, Start over, and the key-event shortcut pause playback. Timers are cleaned up on pause, speed changes, selection changes, and unmount.
- Timeline: search by ID, timestamp, player, team, or translated event label; optionally filter by event type. An empty result offers Clear filters. Filtering changes the list only; it does not rewrite canonical prefix statistics or automatically change the selected event.
- Analysis: separate Insight, Evidence, and Trust notes tabs. Evidence values map to the event/statistics fields. The raw source event is inspectable. Trust status means consistency with the synthetic source, not external verification. The fixture's pending team-review status remains visible.
- Sequence snapshot: counts through the selected event only. Accuracy is null/No attempts before a team's first pass. Rewinds and repeated selections use the stored prefix view rather than incrementing totals.
- Agent workflow: three expandable illustrative outputs. No fake timers or simulated agent activity are displayed. Raw JSON uses the API's field names and source values, even when the surrounding interface is French.
- API connection: the sidebar opens the existing health check on demand. An unavailable backend does not prevent sample exploration. This is a health request only; no processing endpoint is called in Task 5.

The interface uses responsive layouts, visible keyboard focus, native controls, SVG text descriptions, a skip link, and tabs with Arrow Left/Right and Home/End navigation. Reduced-motion preferences disable transitions and smooth scrolling. UI text, explanations, limitations, and warnings support English/French; the document language follows the preference.

## Sample provenance and regeneration

`frontend/src/data/dashboard-samples.ts` contains 32 typed examples: eight canonical events × two languages × two audiences. The export script runs the deterministic mock workflow at authoring time, marks every result `result_source: example`, resets trace durations to zero placeholders, and replaces runtime wording with sample wording. It does not need Azure or a running API server. No response example is presented as browser-side execution.

From `backend/`, with the development environment activated:

```bash
python scripts/export_dashboard_samples.py --check
python scripts/export_dashboard_samples.py
```

Use the second command after changing the canonical fixture or mock narrative. Commit the generated TypeScript with those changes, then run frontend lint/build. The generator is deterministic and revalidates every response with Pydantic. Its tests check complete coverage, illustrative provenance, identical facts across preferences, and reproducibility.

## Acceptance checks

| Action | Expected result |
| --- | --- |
| Open the frontend with FastAPI stopped | Dashboard works; sample provenance is visible |
| Select `evt-064` | 44.28 length, +40 progression, one annotated line, Atlas 4/4 passes |
| Switch Fan/French | French explanation and labels; unchanged geometry, evidence, and totals |
| Select `evt-063` | Backward progression −7; zero annotated lines stays zero |
| Select `evt-065` | Failed pass, dashed arrow/cross, no completed gain claimed |
| Select `evt-066` or `evt-068` | Point marker; pass metrics Not applicable |
| Select `evt-067` | Right-to-left pass, +16 progression, unknown pressure/lines, limited context |
| Select final event, then first, then key event | Prefix totals return to 8, 1, and 4 events respectively |
| Play at 4× | Sequence advances using source gaps and stops at 63:38 |
| Pause, seek, or select an event | Playback pauses; pitch and all panels show the same event |
| Search for a nonexistent player | Empty state; Clear filters restores the events |
| Filter to Recovery | Only `evt-068` appears; selected analysis/totals are unchanged until selection |
| Use the evidence tabs with arrow keys | Focus and active panel move together |
| Expand a sample agent output | Inspectable JSON; no live runtime duration claimed |
| Open API connection with FastAPI stopped | Clear unavailable state; dashboard remains usable |
| Resize to small mobile/tablet widths | Controls remain usable, with no horizontal page overflow; timeline scrolls within its own track |

Automated checks:

```bash
# In frontend/
npm run lint
npm run build
```

```bash
# In backend/
python -m pytest -q
python scripts/export_dashboard_samples.py --check
python scripts/export_contract.py --check
```

Browser QA covered the main interaction cases, both presentation preferences, replay completion/pause/seek, evidence keyboard navigation, filters, sample outputs, optional offline diagnostics, and 320/390/768-pixel preview frames plus the desktop layout. A narrow-page overflow defect was corrected during these checks.

The browser screenshot in `docs/screenshots/dashboard-desktop.jpg` records the completed desktop sample view.

## Remaining milestones

Task 6 adds the Azure backend adapter and [environment/live-access checks](azure-setup.md); the subscription owner must run the live preflight. Configuring Azure does not change this dashboard's sample mode. Task 7 replaces preloaded view selection with typed REST requests, loading/error states, cancellation, and stale-response protection while preserving provenance and fallback visibility. It must distinguish runtime results from sample data rather than presenting the stored examples as live AI.

Official implementation references: [React effect cleanup](https://react.dev/reference/react/useEffect) and [WAI-ARIA tabs keyboard interaction](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/).

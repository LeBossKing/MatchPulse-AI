# Task 8: scenario testing and bug fixing

Use this checkpoint after the Task 7 integration works. Member 1 owns technical checks and fixes, Member 2 validates the source annotations and tactical claims, and Member 3 rehearses and records acceptance results.

The [Member 2 validation guide](member2-validation.md) maps the imported 27 proposals to 19 current-MVP controls and 8 deferred source cases. The full runner also verifies this scope map and the original handoff's manifest. Record human source/tactical review in [the pending review form](data-validation.md).

## Run the automated checks

Install development dependencies once:

```bash
# From the repository root; keep the existing backend/.env.
cd backend
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cd ../frontend
npm ci
cd ..
```

Then, from the repository root:

```bash
python scripts/verify_demo.py
```

The runner stops on the first failed check and returns a nonzero exit code. Its seven checks cover Member 2 scope/manifest consistency, backend tests, generated contracts, generated samples, frontend tests with real HTTP enabled, lint, and the production build. It does not install packages or edit configuration.

The test processes override provider settings and credentials. Mock workflow tests and an intentionally unconfigured Azure fallback are local; no model request is sent. Your running development backend and its environment file are left alone. Integration tests allocate temporary local ports and stop only the processes they start.

To run only the frontend and connected tests, from `frontend/`:

```bash
MATCHPULSE_RUN_API_TESTS=1 npm run test
```

The ordinary `npm run test` skips tests requiring Python. The real HTTP suite checks all 32 event/audience/language combinations using the actual TypeScript client. The connected rehearsal renders the real React app in jsdom, talks to FastAPI through real HTTP, inspects evidence and traces, checks personalization and sequence statistics, and stops/restarts FastAPI to test recovery. It also verifies actual backend configuration fallback. jsdom is not a browser layout or CORS enforcement test; a separate HTTP test verifies the CORS preflight headers.

## Rehearse on the configured machine

Start both apps as described in [runtime integration](integration.md). Use API mode with the verified Azure deployment. Check the browser developer tools Network panel when recording results; `/health` alone does not prove Azure execution.

| Check | Action | Expected result |
| --- | --- | --- |
| Main event | Select `evt-064` in Analyst/English. | `AZURE · RUNTIME`, length 44.28, progression +40, one annotated line, Atlas 4/4, Harbor 0/0. Three completed stages with measured durations; tactical trace has actual provider `azure` and null fallback reason. |
| Audience and language | Choose Fan and French. | French narrative and interface, decimal display 44,28; the event, geometry, evidence values, and prefix counts keep the same meaning. |
| Evidence and trust | Open Evidence, Trust notes, and runtime output. | Every displayed fact has a source value; source data remains synthetic and pending review until Member 2 approves it. No unsupported chance, xG, tracking, or midfield claim. |
| Failed attempt | Select `evt-065`. | Unsuccessful pass; Atlas 4/5 and 80%. Endpoint progression +11 describes the recorded attempt, not retained possession. |
| Opposite direction and missing annotations | Select `evt-067`. | Harbor progression +16 despite decreasing x. Pressure is Unknown, lines show ?, validation is Limited context. Unknown is not represented as zero. |
| Regains and final totals | Select `evt-066`, then `evt-068`. | Point overlay; pass length/progression/lines are not applicable. Final totals: Atlas 4/5 (80%), Harbor 1/1 (100%), Harbor one interception, Atlas one recovery. |
| Cache and rewind | Return to the same `evt-064` preferences. | Cached API result when revisited within five minutes. Atlas returns to 4/4; repeated selections do not accumulate statistics. Run analysis again makes a fresh request. |
| Rapid selection | Select several events quickly while processing. | Previous analysis disappears immediately. Late replies never replace the newly selected event's result. |
| Replay | Start at the first event, choose 4x, play, pause, and seek. | Replay follows source order, waits for each analysis, stops at the final event, and pauses on an API error. Runtime processing affects replay duration. |
| Filtering and keyboard | Search for an absent player, clear filters, and change event type. Navigate analysis tabs with arrow keys, Home, and End. | Clear empty state, all eight events recover, filtering does not run analysis, tab focus and selected panel agree. |
| API outage and retry | Stop your development FastAPI process and click Run analysis again. Restart it and click Retry. | Explicit API error, blank previous metrics, no runtime traces from an old selection; retry restores an actual response. A cached view alone does not test the outage. |
| Explicit offline mode | With FastAPI stopped, deliberately select Samples. Then restart FastAPI and return to API mode. | SAMPLE DATA is visible and selections make no processing requests. Returning to API mode loads fresh canonical data and performs runtime analysis. |
| Responsive layout | Check desktop, 768px, 390px, and 320px in English and French. | Readable controls, pitch, timeline, notes, and traces; no page-level horizontal overflow. |

If Azure falls back during the main check, record the fallback reason and fix deployment/configuration/access before marking the Azure demonstration as passed. A successful fallback remains a valid recovery result.

## Record results and fix failures

Development verification on 2026-10-24 passed: 170 backend tests, 37 frontend tests including all five opt-in connected tests, contract and sample checks, lint, and production build. The 32 request variants are exercised inside the HTTP tests. No application defect was reproduced in this automated rehearsal. The sample-mode regression test now waits for the loaded dashboard's provenance badge instead of accepting the bootstrap heading as completion.

These results use local mock/configuration-fallback execution. The manual live-Azure, browser-layout, source-review, and final video rehearsal gates remain separate.

The Member 2 rule update was verified on 2026-10-27: all seven runner checks passed, with 195 backend tests and 37 frontend tests. The 19 adapted controls refer to current-MVP coverage; the eight source-specific cases remain deferred. This does not change the original research test matrix or complete the human review.

For each failure, record the commit, language/audience, event ID, steps, expected/actual behavior, browser, HTTP status, and safe provider reason. Keep one issue per reproducible bug. Recheck the failed scenario after a fix and rerun the automated runner when code or contracts change. Do not include keys or authorization headers in bug reports.

| Gate | Current evidence / owner |
| --- | --- |
| Automated scenario checks | Run the command above on the final Task 8 commit and record its exit status. |
| Live Azure dashboard | User reported Task 7 working; Member 1 reruns the main acceptance on the recording machine. |
| Source and tactical review | Pending Member 2 approval; automated consistency checks do not grant tactical approval. |
| Final demo rehearsal | Member 3 records the manual checklist and video timing after the final commit. |

Task 8 is complete when automated checks pass, the manual scenario passes on the demonstration machine, and any blocking bugs are fixed. Then use [the demo script](demo-script.md) for Task 9 pitch and recording preparation.

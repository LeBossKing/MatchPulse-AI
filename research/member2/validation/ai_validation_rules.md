# MatchPulse AI — Evidence & AI Validation Rulebook (Member 2, Step 6)

**Scope:** Turkey–Italy, StatsBomb Open Data match `3788741`, five event IDs in Step 4. These are implementation requirements and test specifications, **not tests already run against the application**.

## Agent responsibilities

- **Agent 1 — Match Intelligence:** parse and validate events; derive deterministic facts; return provenance, units, and explicit `null` for unavailable tactical metrics.
- **Agent 2 — Tactical Explainer:** produce narrative constrained to Agent 1 facts; distinguish evidence from interpretation; skip simple events when configured.
- **Agent 3 — Trust & Personalization:** check each claim against source evidence and Agent 1 facts; remove or reject unsupported claims; adapt Fan/Analyst and EN/FR without changing facts.

## Rules

| ID | Requirement | Expected handling |
|---|---|---|
| R01 | Source-grounded claim | Every factual assertion must be linked to a real event field or a verified deterministic computation. Reject ungrounded claims. |
| R02 | Structural integrity | Verify event ID, event type, location arrays and numerical range (StatsBomb x: 0–120, y: 0–80), required values, and linked IDs before derivation. Invalid input: clear error/insufficient-data state. |
| R03 | Units and precision | Raw geometry uses StatsBomb coordinate units. Use `sqrt((x2-x1)^2+(y2-y1)^2)` and attacking-direction-adjusted x progression; do **not** label raw units metres. Use stated rounding tolerance. |
| R04 | Outcomes and links | Treat pass outcomes using dataset convention; link shots only through verified `assisted_shot_id` that exists in source and is a Shot; never invent a goal or guaranteed scoring chance. |
| R05 | Tactical uncertainty | Missing `under_pressure` is **not** proof of no pressure; 360 freeze frames show visible players, not full tracking. No automatic inference of exactly N lines broken. Unknown tactical metric must remain `null`/undetermined. |
| R06 | Missing fields | Do not fabricate absent information. Omit affected claim; report limitation. Missing mandatory coordinates may make distance/progression unavailable. |
| R07 | Personalization invariance | Fan/Analyst and EN/FR can vary detail, not underlying data values, identities, outcomes or event selection. |
| R08 | Interpretations | Tactical significance may be qualified as interpretation; remove absolute causal/guaranteed claims. |
| R09 | Model fallback | On Azure timeout/error or no credentials: return clearly labelled template/mock output and an accurate execution trace; never claim live model inference. |
| R10 | UI state | Changing presentation options must not re-count statistical events or silently change selection. |

## Acceptance principles

1. **Exact text matching is not required.** Validate semantic propositions, identities, units and evidence; translation and narrative wording are allowed to vary.
2. **Pass/outcome conventions:** a missing `pass.outcome` in StatsBomb data usually indicates a completed pass. Special cases (e.g., set pieces and other event semantics) must be handled explicitly in aggregate metrics.
3. **Line-breaking:** StatsBomb specifies a completed pass that progresses ≥10% closer to goal and intersects/gets behind an opponent defensive line. Raw open-data 360 snapshots alone do not certify a StatsBomb provider-generated line-breaking label. Do not convert our visual review's *inconclusive* classification into `true`.
4. **Warning vs failure:** when context is merely absent, display a limitation; when supplied data are contradictory, fail validation or rewrite.
5. **Fixture mutations:** tests simulate altered copies of source events; never overwrite original StatsBomb files.

## Evidence and references

- Original match data: https://github.com/statsbomb/open-data (usage terms and attribution in repository README).
- Hudl StatsBomb's published line-breaking definition: https://statsbomb.com/articles/soccer/statsbomb-360-analysing-line-breaking-passes-in-liga-mx/
- Hudl Support 360 fields and metrics: https://support.hudl.com/s/article/access-event-data-metrics-360-python?language=en_US
- Decroos et al. (2019), *Actions Speak Louder than Goals*, https://doi.org/10.1145/3292500.3330758 — background research on contextual action evaluation, not the source of our pass-distance geometry.

## Execution protocol

For each case in `ai_test_cases.json`, select the source event, deep-copy it, apply `input_mutation` in a test environment, call `/events/process` with the specified audience/language, inspect the three-agent trace, and compare facts/claims with `expected`. Record actual results in `test_matrix.csv`. Field-level input mutation requires a test fixture endpoint or injection harness; the production API may only accept an event ID. Test cases concerning a fabricated explanation require a validator unit-test seam. `provider_status` and `ui_action` are simulated conditions, not actual JSON event fields.

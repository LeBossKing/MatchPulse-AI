# MatchPulse AI — Member 2 Step 4: Football metrics and scientific validation

**Dataset:** StatsBomb Open Data, Turkey vs Italy, match `3788741`. Source JSON files: `events/3788741.json` and `three-sixty/3788741.json`. Five passes taken from the previously documented tactical shortlist; results in `metrics_validation.csv`. **Status:** deterministic baseline metrics validated, tactical line-breaking unresolved.

## Data conventions and scope

- Raw StatsBomb event locations use its **120 × 80 coordinate scale**. For this deliverable geometric distance and forward change are explicitly in **coordinate units**, not metres. `pass.length` is provider-reported; comparison against coordinate geometry validates data consistency but does not independently establish physical distance.
- In these event records each pass is viewed on its own team's attacking-coordinate frame (toward increasing x); `end_x - start_x` is therefore a usable forward progression proxy for these five actions. Do not assume raw global pitch orientation is standardized for mixed providers. Use documented conversion if integrating SPADL (105m × 68m).
- Count raw `type.name == "Pass"` events, **including set-piece/restart passes**. Alternative provider conventions may exclude them. This is an explicit project definition, not a universal official KPI.
- Successful/complete pass: `pass.outcome` **absent**, as encoded in this match's StatsBomb events; unusual outcomes such as `Unknown` should be checked separately for other datasets. Do **not** count separate `Ball Receipt*` events as extra passes.
- A missing `under_pressure` field means **no affirmative pressure annotation in this record**, not proof there was no opponent near the player or that physical pressure was zero.
- `360.freeze_frame` is partial visible-player context, **not continuous full-squad tracking**. Do not assert exact number of defensive lines beaten from these samples.

## Metric specifications

| Metric | Definition / equation | Required fields | Output | Restrictions |
|---|---|---|---|---|
| Pass distance (coordinate) | `sqrt((end_x-start_x)^2+(end_y-start_y)^2)` | `location`, `pass.end_location` | 120×80 coordinate units | 2D straight-line displacement, not 3D ball flight or physical metres |
| Recorded pass length | `pass.length` | `pass.length` | source value | Provider-derived, check agreement with geometric coordinates |
| Forward progression | `end_x - start_x` | both x coordinates | coordinate units, may be negative | Direction convention must be documented |
| Pass completion (%) | `100 * (# Pass events without pass.outcome) / (# Pass events)` | `type`, `pass.outcome`, team | percent | Raw passes incl. restarts; not an open-play-only rate |
| Under-pressure annotation | `true` if `under_pressure is true`; otherwise `not affirmatively annotated` | `under_pressure` | categorical | Cannot infer intensity from Boolean |
| Shot assist annotation | `pass.shot_assist is true` and optionally linked `assisted_shot_id` | pass fields, shot event | categorical and traceable shot ID | A shot assist is not the same as a goal assist |
| Line breaking | **Not calculated for MVP** | validated defender geometry and line algorithm | `null/undetermined` | No reproducible/verified classifier agreed upon |
| Progressive pass category | **Not calculated for MVP** | explicit chosen threshold & direction rules | `null` | Positive dx alone is not an official progressive-pass label |

## Deterministic quality checks and interpretation

1. Recompute coordinate distance and compare with `pass.length` (`length_absolute_difference` in CSV). Note the units and provider field origin.
2. Preserve raw numeric precision and round **only at report/display time**.
3. Verify `assisted_shot_id` resolves to a `Shot` event; keep both IDs for evidence citations.
4. Do not confuse `under_pressure` annotation with a calculated pressure score.
5. Distinguish fact from inference: positive x displacement is observed; “dismantled the defensive press” requires more evidence.
6. Validate missing values without silently imputing pressure, defenders, distances, or labels.

## Research grounding

- **StatsBomb Open Data**, repository and terms: https://github.com/hudl/open-data . Attribution and logo are requested for published/shared insights.
- **StatsBomb Open Data specification**, repository `doc/` directory: https://github.com/hudl/open-data/tree/master/doc . Source for JSON structure and field semantics.
- **Decroos et al. (2019)**, *Actions Speak Louder than Goals: Valuing Player Actions in Soccer*, https://doi.org/10.1145/3292500.3330758 . Research context for standardized football actions; **does not prescribe our raw-pass denominator**.
- **socceraction SPADL documentation**: https://socceraction.readthedocs.io/en/latest/documentation/spadl/spadl.html . 105×68m standardization; different from raw StatsBomb.
- **StatsBomb 360 line-breaking discussion**: https://statsbomb.com/articles/soccer/statsbomb-360-analysing-line-breaking-passes-in-liga-mx/ . Methodological context, **not evidence of a line-break in this match**.

## Handoff for Member 1

Use `expected_agent_facts.json` as deterministic reference fixtures for the five shortlisted passes, and `metrics_validation.csv` for unit tests. Map fields to your agreed API schema; **do not expose `line_breaking=true`** from these fixtures. If UI should show physical metres, first establish and document a defensible coordinate conversion. All outputs based on real football data should credit **StatsBomb**.

## Known limitations

- Reproducible pass-completion rate depends on including all restart passes; use the same denominator across backend/UI.
- Source-specific annotations should not be treated as measured probabilities or independent causal evidence.
- The 360 captures are snapshot observations with variable visibility; no explicit validated defensive-line grouping was available.

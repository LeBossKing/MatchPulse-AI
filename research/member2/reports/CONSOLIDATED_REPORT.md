# MatchPulse AI — Member 2 consolidated research & developer handoff

**Version:** 1.0 | **Source:** StatsBomb Open Data, Turkey vs Italy, match 3788741 | **Scope:** Football data research, proposed story detection, evidence validation and development handoff.

## Executive summary

This package consolidates the real-match reference data, 3 selected tactical stories, documented calculations, 20 reference explanations and 27 prewritten AI test cases. It adds a concrete five-category story detection design, a configurable heuristic ranking policy and an illustrative story API response. This is **not** evidence that the app, Azure models or automatic detection have already executed.

## Verified source-data checks performed for this handoff

- Event records: **3,803**; 360 snapshots: **3,370**.
- All **3** story fixtures passed checks that referenced event IDs exist and are in ascending source `index` order.
- 360 IDs linked to the event file: **3,370/3,370**.
- Story fixture event counts: story_001=12, story_002=19, story_003=14.
- Source events preserve period-relative `timestamp` and full-match `minute` separately. Do not treat `00:33:24` for period 2 as minute 33.

## Three reference tactical stories

| Story | Observed period / match minute | Outcome | Purpose |
|---|---|---|---|
| story_001 | period 2 / 78:24–78:30 | Recorded Italy goal | Shot buildup after regain |
| story_002 | period 1 / 44:17–44:33 | Shot off target | Regain and chance-building |
| story_003 | period 2 / 51:45–51:51 | Miscontrol | Playing under recorded pressure |

Selected sequence descriptions are supported by specific event IDs in `data/three_tactical_stories.json`; causal language about defensive structure or pressure impact is intentionally limited.

## Deliverables and ownership

| Path | Use by Member 1 | Status |
|---|---|---|
| `discovery/story_discovery_rules.md` | Implement five candidate detectors | **Proposed rules** |
| `discovery/story_ranking_rules.json` | Implement deterministic candidate ranking | **Heuristic, needs agreement** |
| `data/three_tactical_stories.json` | Reference scenarios and replay | Source-traced fixtures |
| `data/expected_agent_facts.json` | Agent 1 regression assertions | Reference facts |
| `explanations/expected_explanations.json` | Language/mode reference outputs | 20 manually authored references |
| `validation/ai_validation_rules.md` | Trust Agent requirements | Proposed validation specification |
| `validation/ai_test_cases.json` | Agent workflow tests | 27 cases, **not executed** |
| `contracts/api_example.json` | Backend/frontend alignment | **Proposal, not running API** |
| `visuals/` | Illustrative dashboard graphics | Static images from event/360 data |

## Implementation acceptance criteria

1. Same input data yields stable source event IDs, deterministic numeric facts and explicit selection reasons.
2. The detector finds candidate narratives beyond forward/line-breaking passes: goals, shots, recoveries and under-pressure sequences.
3. No unverified line-breaking count, psychological intent or causal pressure explanation is asserted as fact.
4. Fan and Analyst output, and EN/FR, may change presentation but not underlying facts.
5. The interface exposes evidence IDs, backend execution status and a clearly labelled mock fallback.
6. Test the 27 specifications against the actual running API before declaring pass/fail.

## Critical limitations

- The open 360 freeze-frames capture a subset of visible players and are not full tracking. The package does **not** include a verified line-breaking classifier.
- Ranking thresholds/weights are local engineering decisions, **not scientifically calibrated**.
- Pass-length values are native StatsBomb units, not physical metres; provider xG is model supplied, not newly trained.
- Generated/static reference explanations are not proof of successful LLM execution. Integration testing remains pending.
- Original large event and 360 files are excluded from this ZIP for size and licensing clarity. Official provenance: https://github.com/statsbomb/open-data/tree/master/data . Retrieve `events/3788741.json` and `three-sixty/3788741.json`, keeping the matching UUIDs.

## Literature / methods references

- StatsBomb Open Data official repository and usage terms: https://github.com/statsbomb/open-data
- Decroos et al. (2019), *Actions Speak Louder than Goals*, DOI https://doi.org/10.1145/3292500.3330758
- socceraction SPADL and expected-threat technical documentation: https://socceraction.readthedocs.io/en/latest/
- StatsBomb 360 line-breaking discussion: https://statsbomb.com/articles/soccer/statsbomb-360-analysing-line-breaking-passes-in-liga-mx/

## Next decisions requiring Member 1

- Approve the proposed schema or map it onto existing Pydantic models and `/events/process` route.
- Confirm whether the prototype will calculate story scores on the backend or use preselected fixtures in the demo.
- Provide a running app or API responses for end-to-end testing.

# Automatic tactical-story discovery — proposed specification v1.0

**Status:** Proposed implementation rules from Member 2, not published provider categories or verified AI outputs. Match identifier `3788741` (Turkey–Italy). Obtain Member 1 approval before freezing the contract. Keep the original StatsBomb event UUID as provenance.

## Data requirements and guardrails

- Consume events in `index` order; group within the same `period` and `possession` and `possession_team.id`. A possession ID is a source grouping, not a guarantee that every micro-event belongs to the same attacking team.
- Store `event_id`, `index`, `period`, `minute`, `second`, `timestamp`, `team.id`, `player.id`, `type.name`, `location`, subtype/outcome, `under_pressure` and `related_events` when present.
- A shot must be verified by an actual `Shot` event, a goal by `shot.outcome.name == "Goal"`, and a pass assist by source linkage such as `pass.assisted_shot_id` where present.
- Absence of `under_pressure` means **not annotated**, never “no pressure.” 360 visibility is partial; do not infer all defensive lines from one freeze-frame.
- Do not confuse period-relative `timestamp` with match-global `minute`; in second half, `00:33:24` can mean match minute 78.
- Coordinates use StatsBomb 120 × 80, and are not physical metres. Never assert line-breaking without an independently reviewed defender-based classifier.

## Five story types and exact proposed rule logic

1. **shot_creation**: a possession group contains one or more `Shot` events; select the preceding 5–20 seconds of same-possession events, minimum 2 relevant ball actions. Source `pass.assisted_shot_id` is preferred for direct assist claims. This is candidate shot buildup, not causality proof.
2. **defensive_regain_attack**: start at an `Interception` or `Ball Recovery` event attributed to the attacking team, with at least one later `Pass` or `Carry` in the same possession within 20 seconds; outcome may be shot, goal, turnover, or continuation. Confirm interception outcome if populated; do not call every attempt a successful regain.
3. **under_pressure_sequence**: same-possession window ≤15 seconds with at least one `Pass`, `Carry` or `Ball Receipt*` where `under_pressure == true`; describe subsequent event type and outcome without asserting that pressure *caused* it. Prefer ≥2 ball-moving actions.
4. **buildup_progression**: ≥3 ordered successful passes/carries within a single possession and ≥20 native x-units net displacement from first action start to last action end, provided start/end are present. This is a **project screening threshold**, not a standard progressive-pass definition.
5. **possession_breakdown**: a possession window ending with an explicit incomplete pass, miscontrol, dispossession or team change; require at least one earlier action in the same possession. Do not infer sole cause of loss from event adjacency.

## Ranking / deduplication / safety

- Generate candidates per rule; one sequence may receive multiple category tags.
- Ranking configuration lives in `story_ranking_rules.json`; do not describe its weights as scientific estimates or AI confidence.
- Deduplicate overlapping candidate windows on shared source-event IDs (>70% overlap), retaining the higher-ranking candidate and its alternate labels.
- Return evidence IDs and warnings with each story. If data insufficient, return `inconclusive` rather than a fabricated classification.
- Review candidates against reference `three_tactical_stories.json`; the three examples are regression fixtures, not a statistical benchmark for detection accuracy.

## Pseudocode

```python
for (period, possession_id), sequence in chronological_groups(events):
    for category in STORY_RULES:
        for window in detect(category, sequence):
            if required_fields_present(window):
                candidates.append(build_story(window, evidence_event_ids=True))
rank_and_deduplicate(candidates)
```

## Scientific boundaries

Event selection and score weighting above are project design hypotheses requiring validation. For data provenance see https://github.com/statsbomb/open-data ; for action representation see https://socceraction.readthedocs.io/ ; for football-action valuation see Decroos et al., *Actions Speak Louder than Goals* (2019), DOI:10.1145/3292500.3330758. None of these sources establishes the proposed weighting coefficients.

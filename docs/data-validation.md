# Synthetic fixture review record - pending

**Decision: PENDING REVIEW.** This is a form for Member 2, not a completed approval.

| Review field | Value |
| --- | --- |
| Reviewer | To be completed by Member 2 |
| Review date | To be completed |
| Reviewed commit/version | To be completed |
| Dataset | `backend/data/demo_match.json` |
| Match / key event | `match-demo-01` / `evt-064` |
| Decision | Pending; record Approved or Corrections required after review |

## Proposed reference facts to check

The values below describe the current authored fixture and its calculations. Their inclusion here does not constitute human tactical approval. Distances use normalized pitch units, not metres.

| Event | Time | Proposed source action | Length | Forward progression |
| --- | --- | --- | ---: | ---: |
| evt-061 | 63:08 | Atlas 02 completes to Atlas 07 | 9.85 | +9 |
| evt-062 | 63:14 | Atlas 07 completes to Atlas 06 | 8.06 | +7 |
| evt-063 | 63:18 | Atlas 06 completes backward to Atlas 07 | 8.06 | -7 |
| evt-064 | 63:24 | Atlas 07 completes to Atlas 11 | 44.28 | +40 |
| evt-065 | 63:28 | Atlas 11's intended pass to Atlas 09 fails | 14.21 | +11, attempted endpoint displacement |
| evt-066 | 63:29 | Harbor 04 interception | Not applicable | Not applicable |
| evt-067 | 63:34 | Harbor 04 completes right-to-left to Harbor 08 | 21.93 | +16 |
| evt-068 | 63:38 | Atlas 06 recovery | Not applicable | Not applicable |

At the main event, Atlas has 4/4 completed passes and Harbor no attempts. Final sequence totals are Atlas 4/5 (80%), Harbor 1/1 (100%), Harbor one interception, and Atlas one recovery. Counts describe the selected sequence prefix, not the full match.

## Review checklist

- [ ] Chronology, intended receivers, player/team identities, and possession transitions are plausible.
- [ ] The normalized 0-100, top-left coordinate convention and opposite attacking directions are consistent.
- [ ] The main event selection and numerical reference values are correct.
- [ ] Pressure levels and the main event's one-line annotation have an explicit, defensible meaning as fictional authored annotations.
- [ ] A line annotation does not establish a particular midfield/defensive formation line or defender positions.
- [ ] Missing annotations for evt-067 remain unknown; positive progression does not imply a shot or goal.
- [ ] Failed attempts, backward passes, interceptions, and recoveries retain their source meaning.
- [ ] Fan/Analyst and EN/FR outputs retain the same facts and appropriate uncertainty.

## Corrections and interpretation notes

To be completed. For each correction, include the event ID, original value/wording, replacement, and reason. Separate source annotations from calculated metrics and permitted tactical interpretation.

## Final decision

To be completed by Member 2, including reviewer name/date and the exact reviewed version. Keep the application's `review_status` pending until this decision exists. Implement any accepted corrections and update affected exports/tests before recording the final demo.

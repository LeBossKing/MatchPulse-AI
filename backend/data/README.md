# Synthetic demo fixture

`demo_match.json` is the canonical source for the demo endpoints. It is authored fictional data and is currently **pending Member 2 review**.

Teams and players are fictional labels. The roster is deliberately partial. The score is the context at the start of this excerpt. This is not a full match or an external data feed.

| Event | Time | Action |
| --- | --- | --- |
| evt-061 | 63:08 | Atlas 02 completes a pass to Atlas 07. |
| evt-062 | 63:14 | Atlas 07 completes a pass to Atlas 06. |
| evt-063 | 63:18 | Atlas 06 completes a backward pass to Atlas 07. |
| **evt-064** | **63:24** | **Atlas 07 completes the main forward pass to Atlas 11, with synthetic high-pressure and one-line-break annotations.** |
| evt-065 | 63:28 | Atlas 11 attempts an unsuccessful pass to Atlas 09. |
| evt-066 | 63:29 | Harbor 04 records an interception. |
| evt-067 | 63:34 | Harbor 04 completes a right-to-left pass to Harbor 08, without tactical annotations. |
| evt-068 | 63:38 | Atlas 06 records a recovery. |

The main pass is from `(27,58)` to `(67,39)`: expected distance **44.28 normalized units** and forward progression **40 units**. Its line-break annotation does not identify a specific midfield/defensive formation line or provide player tracking.

For future prefix statistics at evt-064: Atlas 4/4 completed passes, Harbor no attempts. At the end of the excerpt: Atlas 4/5, Harbor 1/1; Harbor has one interception and Atlas one recovery.

## Member 2 review

Before changing `review_status` to `approved`, confirm:

- Event chronology, intended receivers, identities, team membership, and possession transitions.
- Absolute coordinate convention and attacking directions for period 2.
- Meaning and plausibility of the authored pressure and line-break annotations.
- Main event selection, expected calculations, and permitted/unsupported tactical claims.
- Coverage of the successful pass, failed pass, backward pass, regain, and missing-data cases.

Run the backend contract tests after editing the fixture. Keep `review_status: pending_review` until the review actually happens. The fixture is cached per process; restart the backend after editing it.

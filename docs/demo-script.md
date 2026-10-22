# Demo plan - draft

The final submission video targets 110-115 seconds. The team must validate the synthetic event sequence and factual claims before recording.

## Main story

Show a successful forward pass, explain the available evidence, and adapt the insight for Analyst and Fan audiences in English and French. A claim that the pass bypassed a midfield line requires an explicit source annotation or suitable defender-position data.

Member 2 provides the validated fixture and expected facts. Member 3 finalizes the acceptance checklist, narrative, and video timing. Member 1 implements the scenario.

## Planned sequence

| Time | Demonstration |
| --- | --- |
| 0-15 s | Introduce the problem and MatchPulse AI. |
| 15-35 s | Select the main event and show its trajectory. |
| 35-60 s | Explain calculated facts and supporting evidence. |
| 60-80 s | Switch audience mode and language. |
| 80-100 s | Inspect the actual agent trace and a missing-data example. |
| 100-115 s | State the benefit and technologies actually implemented. |

## Foundation acceptance check (current checkpoint)

1. Start both apps with the documented commands.
2. Open the frontend and verify `Backend connected` with the expected API metadata.
3. Stop FastAPI and retry: the UI reports `Backend unavailable`.
4. Restart FastAPI and retry: the UI recovers.
5. Verify the page at desktop and mobile widths.

The foundation screen is a development checkpoint. Match analysis and model execution will be demonstrated after the later implementation tasks are complete.

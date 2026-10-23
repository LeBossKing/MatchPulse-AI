# Demo plan - draft

The final submission video targets 110-115 seconds. The team must validate the synthetic event sequence and factual claims before recording.

## Main story

Show a successful forward pass, explain the available evidence, and adapt the insight for Analyst and Fan audiences in English and French. The proposed fixture uses the pass at 63:24 (evt-064), annotated as bypassing one opposition line. Identifying that line specifically as midfield would require additional source evidence.

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

## Foundation acceptance check

1. Start both apps with the documented commands.
2. Open the frontend and verify `Backend connected` with the expected API metadata.
3. Stop FastAPI and retry: the UI reports `Backend unavailable`.
4. Restart FastAPI and retry: the UI recovers.
5. Verify the page at desktop and mobile widths.

The foundation screen is a development checkpoint. Match analysis and model execution will be demonstrated after the later implementation tasks are complete.

## Task 3 checkpoint

The read endpoints supply the proposed fixture and initial statistics. The eight JSON examples define the output shape and presentation variants; they are not evidence of agent execution. Member 2 reviews the fixture and claims before the team finalizes the demo story.

## Task 4 checkpoint

Run the Postman collection or use Swagger to process `evt-064`. Expect HTTP 200, length 44.28 normalized units, progression +40, and three measured mock stage traces. Switch to Fan/French and verify unchanged source facts. Process `evt-067` to show missing annotations and a limited validation result; process `evt-065` to preserve the unsuccessful outcome. Return to `evt-064` and confirm its prefix statistics have not increased.

This checkpoint uses deterministic Python rules and templates. No LLM or Azure request is executed. Selecting the future Azure provider returns an explicitly labelled mock fallback. The React screen still checks the backend connection; dashboard construction and its processing controls follow in Tasks 5 and 7.

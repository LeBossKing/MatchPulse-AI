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
2. Open the frontend, click **API connection**, and verify `Backend connected` with the expected API metadata.
3. Stop FastAPI and retry: the UI reports `Backend unavailable`.
4. Restart FastAPI and retry: the UI recovers.
5. Verify the page at desktop and mobile widths.

The optional health panel is a development checkpoint. Its connection state is separate from the dashboard's sample-data mode.

## Task 3 checkpoint

The read endpoints supply the proposed fixture and initial statistics. The eight JSON examples define the output shape and presentation variants; they are not evidence of agent execution. Member 2 reviews the fixture and claims before the team finalizes the demo story.

## Task 4 checkpoint

Run the Postman collection or use Swagger to process `evt-064`. Expect HTTP 200, length 44.28 normalized units, progression +40, and three measured mock stage traces. Switch to Fan/French and verify unchanged source facts. Process `evt-067` to show missing annotations and a limited validation result; process `evt-065` to preserve the unsuccessful outcome. Return to `evt-064` and confirm its prefix statistics have not increased.

Keep `LLM_PROVIDER=mock` for this checkpoint: it uses deterministic Python rules and templates without an external model request. Task 6 adds an optional Azure provider. Task 5 introduced preloaded samples; Task 7 now connects API mode to runtime processing.

## Task 5 checkpoint

The dashboard opens on `evt-064` at 63:24. Show the pitch trajectory and the 44.28 / +40 / 1 metrics, then switch to Fan and French. Open Evidence and Trust notes, select the missing-data event `evt-067`, and inspect its unknown annotations. Select a regain to show a point overlay, then jump back to the key event. Expand a sample agent output and show the sample-data label.

Use replay to step through the source sequence, or filter the timeline by action/player. The dashboard works with FastAPI stopped. Every trace is illustrative and no agent/model is executing in the browser. Keep this distinction explicit in rehearsal; use API mode for the connected demonstration and Samples for this offline checkpoint.

## Task 6 checkpoint

Follow [Azure setup](azure-setup.md), then run `python scripts/check_azure.py --live` from `backend/`. Expect `status: live_verified`, `provider: azure`, and `validation_status: validated`. This explicit check sends one actual request and never substitutes a mock candidate. Check subscription credit and deployment quota separately in Azure.

Set `LLM_PROVIDER=azure`, restart FastAPI, and process `evt-064` through Postman. Inspect `provider: azure` and the tactical trace's actual provider. Geometry and trust checks run locally; Azure supplies the structured candidate and approved templates render the final text. A labelled fallback is a recovery path, not evidence of Azure execution. The dashboard now starts in API mode; Samples remains a deliberate offline option.


## Task 7 checkpoint

Start FastAPI with the configured provider, then open the React dashboard in API mode. Confirm the main event has a runtime provider badge and measured traces. Change audience/language and choose `evt-067` to show limited context, then a regain to show null pass metrics. Revisit a prior selection and identify its cached result; use **Run analysis again** for a new execution.

Replay waits for each API result before continuing. Rapid manual selections must never display a previous event's explanation under the new event. Stop FastAPI and rerun an analysis to show an explicit error, then deliberately select **Samples** to demonstrate the independent offline examples. Restart FastAPI and return to API mode. Include the provider and cache provenance in the recording; source events remain synthetic and pending team review until approved.

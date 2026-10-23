# Illustrative processing responses

These files specify the **future** 200 response for `POST /events/process`. They are static contract examples, not recorded agent runs. The Task 3 endpoint returns 501 for a valid request.

- `main-{analyst,fan}-{en,fr}.json`: the same source event and evidence under four presentation settings.
- `unsuccessful-pass.json`: source failure preserved, without a fabricated completed line break.
- `missing-annotations.json`: a right-to-left pass with unknown pressure and lines broken.
- `interception.json`, `recovery.json`: point events with null pass metrics.
- `process-request.json`: a valid canonical event selector.

Every illustrative response has `result_source: example`, `provider: mock`, explicit example warnings, and placeholder durations of zero. A future real run must use `result_source: runtime` and actual measured trace data. Importing these files for UI development must display their example status.

The contract tests verify geometry, prefix pass counts, source evidence values, cross-references, overlays, and consistency across the four main-event variants. Pydantic validation is not a guarantee of the truth of arbitrary prose.

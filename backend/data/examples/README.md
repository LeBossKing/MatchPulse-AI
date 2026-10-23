# Illustrative processing responses

These files are the **Task 3 illustrative** 200 responses for `POST /events/process`. They are static contract examples, not recorded agent runs. The Task 4 endpoint runs the mock workflow and returns calculated results; it never loads these examples as runtime responses.

- `main-{analyst,fan}-{en,fr}.json`: the same source event and evidence under four presentation settings.
- `unsuccessful-pass.json`: source failure preserved, without a fabricated completed line break.
- `missing-annotations.json`: a right-to-left pass with unknown pressure and lines broken.
- `interception.json`, `recovery.json`: point events with null pass metrics.
- `process-request.json`: a valid canonical event selector.

Every illustrative response has `result_source: example`, `provider: mock`, explicit example warnings, and placeholder durations of zero. A runtime mock run uses `result_source: runtime` and actual measured traces. Importing these files for UI development must display their example status. Runtime wording and evidence coverage can differ while preserving the source facts.

The contract tests verify geometry, prefix pass counts, source evidence values, cross-references, overlays, and consistency across the four main-event variants. Pydantic validation is not a guarantee of the truth of arbitrary prose.

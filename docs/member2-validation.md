# Task 8: Member 2 rules and final validation

**Current task: 8 - Test the scenario and fix bugs.** Tasks 1-7 are implemented; the automated Task 8 baseline passed. The research handoff is archived on `chore/member2-validation`. This branch accounts for its validation proposals and adds missing applicable regression checks. Task 9 is pitch, documentation, and demo-video preparation.

## Scope of the 27 proposals

The machine-readable [coverage map](member2-rule-mapping.json) accounts for every ID in Member 2's original `ai_test_cases.json`:

| Original IDs | Current treatment |
| --- | --- |
| EV-01 to EV-05 | Deferred source API cases: the five StatsBomb UUIDs are not loaded by the synthetic demo API. |
| CL-01, CL-02, CL-03, CL-04, CL-05 | Adapted controls for unsupported scoring/line/pressure claims, normalized units, and exclusion of unchecked provider prose. |
| CL-06 | Deferred: accepting the real linked-shot statement requires shot-link evidence support. |
| MD-01 | Deferred: removing a StatsBomb assisted-shot link requires a source-adapter fixture. |
| MD-02, MD-03 | Adapted: missing coordinates in an isolated server fixture return typed `500 invalid_fixture` before tactical generation. |
| MD-04, MD-05 | Adapted unknown-annotation grounding controls. The literal 360-frame mutation is not executed because the current MVP has no 360 input. |
| IV-01, IV-02 | Adapted to invalid normalized 0-100 coordinates; the original native-scale inputs are not imported. |
| IV-03 | Adapted to the public selector API's typed unknown-event 404. |
| CT-01 | Adapted: a canonical failed attempt cannot become a completed pass through a provider claim. |
| CT-02 | Deferred: validating a broken StatsBomb assisted-shot link requires source integration. |
| I18N-01, I18N-02, I18N-03 | Adapted to synthetic EN/FR and Fan/Analyst fact/prefix invariance. |
| FB-01, FB-02 | Adapted to actual API timeout/configuration fallback handling with local test providers. |
| STATE-01 | Adapted to backend and rendered React/FastAPI preference/cache/rewind checks. |

There are **19 adapted MVP controls and 8 deferred source cases**. These are scope decisions, not 27 original cases marked as passed. The original research files, test matrix, and source manifest remain unchanged.

The current Tactical Explainer returns structured evidence claims. Unchecked provider text is excluded by the schema; the Trust stage compares structured facts and controlled templates render the final explanation. These tests do not implement a general natural-language fact checker.

## What the new checks verify

- Unknown pressure/line annotations cannot be promoted to known claims in any audience/language variant.
- Unsupported goal or guaranteed-goal claims are rejected.
- API metrics and published EN/FR text keep normalized units.
- Adding unverified prose to a valid-looking candidate causes a visible fallback instead of publishing that prose.
- Missing or invalid server-fixture coordinates prevent tactical generation. Mutations use temporary copies; canonical files are untouched.
- A failed attempt cannot be rewritten as completed.
- An Azure timeout produces disclosed mock fallback with the actual provider and safe reason.

`scripts/check_member2_mapping.py` checks complete/unique case accounting, coverage reference existence, and all 29 original manifest hashes. It does not run source specifications or independently establish tactical correctness.

## Run the checks on your branch

From the repository root, with the existing development dependencies installed:

```bash
python scripts/check_member2_mapping.py
python scripts/verify_demo.py
```

The complete runner now has **seven checks**: scope/manifest consistency, backend tests, generated contracts, generated samples, frontend/real HTTP tests, lint, and production build. It blanks Azure credentials in its test processes. No Azure model request is made.

Development verification on **2026-10-27** passed all seven checks: **195 backend tests and 37 frontend tests**, matching contracts/samples, valid coverage references and original manifest hashes, clean lint, and a successful production build. This adds 25 backend regression cases to the 170-test baseline. The existing Starlette test-client deprecation warning is nonblocking. The eight source-specific proposals remain deferred, and Member 2's fixture review remains pending.

If dependencies need installation:

```bash
cd backend
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cd ../frontend
npm ci
cd ..
python scripts/verify_demo.py
```

## Member 2's review

Give Member 2 `backend/data/demo_match.json`, `backend/data/README.md`, and [the review record](data-validation.md). They review the actual Atlas-Harbor eight-event fixture, record the reviewed commit, their name/date, corrections, and an explicit approval or correction decision.

Approval concerns the fictional scenario and authored annotations. It does not turn synthetic annotations into independently observed football facts. The existing record remains pending until this review is supplied. When approval or corrections arrive, update the fixture, affected examples/samples, and tests together, restart FastAPI, and rerun verification. Some current baseline tests explicitly assert the pending fixture; changing that status alone is incomplete.

## Rehearse on the demonstration machine

Use the existing Azure configuration and the [manual scenario checklist](testing.md). Confirm the main event, Fan/French, missing annotations, failed attempts, regains, replay/cache, and API outage/retry. A fresh tactical trace must show actual provider `azure` with no fallback reason for the Azure demonstration. Cached results and `/health` alone do not prove a new model execution.

Member 3 can prepare the pitch and documentation while these checks run. Record the final video against the chosen tested commit, preserving synthetic-data, provider, and source-review labels accurately.

## Commit and continue

After the automated checks and applicable manual acceptance pass:

```bash
git add backend/tests/test_member2_rules.py scripts/check_member2_mapping.py scripts/verify_demo.py docs
git diff --cached --stat
git commit -m "test: map member 2 rules to MVP validation checks"
git push -u origin test/member2-rules
```

Start Task 9 from this completed branch:

```bash
git switch -c docs/demo-submission
```

Task 9 deliverables are the final README/setup instructions, a truthful architecture and limitations summary, a concise pitch, a timed demonstration script, the recorded demo, and the submission links. Before submission, merge the final reviewed branch into `main` and verify the default branch exposes the complete runnable application.

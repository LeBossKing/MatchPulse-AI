# Source attribution and provenance

![StatsBomb](attribution/statsbomb-logo.png)

**Data source: StatsBomb Open Data (Hudl).** The imported research, tables, reference explanations, tactical-story fixtures, and visualizations use historical Turkey vs Italy match **3788741**. This is real-match reference material; the application's Atlas-Harbor demo fixture is synthetic.

## Official sources and usage references

- [StatsBomb Open Data repository](https://github.com/hudl/open-data) (the former `statsbomb/open-data` address redirects to this repository).
- [Event source: data/events/3788741.json](https://github.com/hudl/open-data/blob/master/data/events/3788741.json).
- [360 source: data/three-sixty/3788741.json](https://github.com/hudl/open-data/blob/master/data/three-sixty/3788741.json).
- [Event and 360 format documentation](https://github.com/hudl/open-data/tree/master/doc).
- [Upstream README and attribution requirements](https://github.com/hudl/open-data#terms--conditions).
- [Upstream data license](https://github.com/hudl/open-data/blob/master/LICENSE.pdf).
- [Official media pack](https://statsbomb.com/media-pack/).
- [Logo copied from the upstream repository](https://github.com/hudl/open-data/blob/master/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png), stored locally as `attribution/statsbomb-logo.png`. Its upstream Git blob is `fc75fa646cba5d0fa9dfcf8b183646b5fe32d8cc`.

The upstream README asks published or shared analyses to identify StatsBomb as the data source and use its logo. Retain that credit when reusing the supplied charts or findings. Upstream data and brand terms remain applicable; the application's code license does not relicense third-party data or artwork. Attribution does not imply StatsBomb endorsement of MatchPulse AI.

## Import record

- Import date: **2026-10-27**.
- Handoff: `MatchPulse_Member2_Developer_Handoff_v1.zip`, prepared by Member 2.
- Application base: `feat/demo-scenario` at `de97c5b9ccdd13001a3fe81dfa06266a5587fe0f`.
- The archive's top-level wrapper directory was removed when placing its contents in `research/member2/`.
- All **30 original files**, including `README.md` and `MANIFEST.json`, retain their exact bytes. All **29 files listed in the original manifest** passed their declared size and SHA-256 checks on import.
- Repository additions are `../README.md`, this attribution page, the local raw-data ignore rule, byte-preservation attributes, and the official logo. They are outside the original handoff's manifest.

The hashes below identify the uploaded files used for this handoff. They are not a claim that the uploads were downloaded at a particular upstream Git commit.

| Uploaded file | Bytes | SHA-256 |
| --- | ---: | --- |
| `MatchPulse_Member2_Developer_Handoff_v1.zip` | 1107442 | `f7641efbb1021047ef9a5901183274e6e1f9aded10fbf3f254a1f49912a4e650` |
| `3788741_events.json` | 3208593 | `b9ddce6bee771bdb1f3564c9ac0552619257e412d0767939f1e7f1500ace3062` |
| `3788741.json` | 6860183 | `2275d616b272f52d863b3ece6dc5d96764f300f4cce30924e98e77b96cc2b5b1` |

## Local raw-data placement

The supplied ZIP intentionally excludes the two large source JSON files. Working copies use the ignored `raw/` directory:

```text
research/member2/raw/3788741_events.json
research/member2/raw/3788741.json
```

The first is the event list; the second is the 360 snapshot list. Copy the supplied uploads to these paths when preparing a fresh checkout. The ignored files are not included in Git commits or the research import download. Use the official source links above to retrieve source data separately, then verify its structure and record the downloaded file hashes.

## Research and execution status

The original package contains 3 source-traced tactical stories, five shortlisted pass fact sets, 20 authored reference explanations, 27 unexecuted AI test specifications, and proposed discovery/ranking/API designs. These labels describe the handoff, not completed runtime execution or a new public API.

Known integration questions from the initial review remain open:

- StatsBomb's native 120-by-80 coordinates and attacking frame require explicit mapping to the current event contract before import into the application.
- Missing `under_pressure` is serialized as `false` in some story entries. Preserve source-field presence and unknown semantics during adaptation.
- The team summary's two Italy goals count shot goals; match-score totals must also account for the own-goal credit.
- The supplied metric-check script expects its input files beside the script; its paths need adaptation to the repository layout before execution.
- Fixture mutations and candidate-claim checks require isolated test seams aligned with the application's structured-candidate workflow.
- Review and approval of `backend/data/demo_match.json` remain a separate Member 2 decision.

The original source files and handoff are preserved so that later corrections, mappings, and executed results can be reviewed separately.

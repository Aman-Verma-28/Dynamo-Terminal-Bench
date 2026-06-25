# dynamo/log-report

A Terminal-Bench 2 (Harbor) task. The agent is given a realistic Apache-style access log and must
produce a six-field JSON summary at `/app/report.json`.

## Overview

The log at `/app/access.log` mixes the combined and common log formats and includes blank lines,
`#` comments, and malformed lines. The agent must parse it and report:

| Field | Meaning |
| --- | --- |
| `valid_requests` | count of well-formed request lines |
| `unique_visitors` | distinct client IPs, **excluding bot user-agents** |
| `top_path` | most-frequent **normalized** path among 2xx/3xx requests (lexicographic tie-break) |
| `total_bytes` | sum of response sizes (`-` counts as 0) |
| `busiest_hour` | busiest clock hour **in UTC** after timezone conversion (earliest-hour tie-break) |
| `error_rate` | fraction of requests with status ≥ 400, 4dp round-half-to-even |

The difficulty is deliberate and lives in *correctness*, not runtime: each field hinges on a precise
rule (bot exclusion, ordered path normalization + status filter, `-`-as-zero, per-line timezone
conversion, banker's rounding). Missing any single rule fails the verifier.

## Approach (reference solution)

`solution/solve.py` is standard-library only: a regex parses each line, invalid lines are skipped,
and the six fields are computed with `datetime`/`timezone` (UTC conversion), `urllib.parse.unquote`
(percent-decoding), and `decimal` (round-half-to-even). `solution/solve.sh` runs it. The oracle is
genuine — no hardcoded answers.

## Environment

`environment/Dockerfile` pins `python:3.13-slim-bookworm` by `@sha256` digest (reproducible) and
bakes the pinned verifier dependencies (`pytest`, `pytest-json-ctrf`). It copies only
`access.log` into the image — no solution or test files leak to the agent. No network access is
required at runtime.

## Verification

`tests/test_outputs.py` has one test per success criterion (valid JSON + the six fields), asserting
the reference solver's known-correct values for the bundled log. `tests/test.sh` runs plain pytest
(deps are already baked in) and writes the reward (`1`/`0`) and a CTRF report to
`/logs/verifier/reward.txt` and `/logs/verifier/ctrf.json`.

Run it:

```bash
harbor run -p log-report -a oracle     # reference solution -> reward 1
harbor run -p log-report --agent nop   # no-op agent        -> reward 0
```

## Difficulty (pass@)

Measured with Terminus-2 + GPT-5.4 (max completion tokens 128000, reasoning effort xhigh):

- Pass@2 @ 900s: _<record after PR run>_
- Pass@8 @ 600s: _<record after PR run — target 1–4/8>_

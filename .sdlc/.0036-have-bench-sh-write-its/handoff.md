---
id: T-0036
title: "Have bench.sh write its exit code and wall-clock duration to the..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0032
---

## Goal
Each bench task's log file (`<bench>/logs/<date>-<task>.txt`) records that task's exit code and wall-clock duration, so a clean-context verifier can check `exit=0` and run time from the log alone.

## Intent
Literal ask: Have bench.sh write its exit code and wall-clock duration to the bench log.
Deltas:
- Which log: defaulted: the per-task log `plugins/sdlc-lite/scripts/bench.sh` already writes (`$bench/logs/$(date +%Y-%m-%d)-$t.txt`), appended after the claude run ends.
- Format: defaulted: one trailer line appended to the log, e.g. `exit=<code> duration=<N>s` (seconds, integer), keeping the existing `exit=` token so greps match; stdout keeps printing it too.
- Date drift: defaulted: compute the log path once per task before the run, so a run that crosses midnight appends to the same file.
- Docs: defaulted: update the bench.sh header comment and any doc that describes bench log contents (CLAUDE.md Commands line, skills/bench, sdlc-lite-author agent) only where they describe what the log holds.
Do: in bench.sh, capture start time and the log path per task, run claude as now, then append `exit=<code> duration=<N>s` to that log and echo the same line to stdout. Keep behavior otherwise identical.
Non-goals: changing bench-summary.sh, runs.jsonl, the /bench skill flow, or task grading.
Done when: a bench.sh run with a stubbed `claude` on PATH (exit code nonzero, e.g. 3) leaves a log whose last line is `exit=3 duration=<int>s`, stdout shows the same line, and `plugins/sdlc-lite/scripts/check.sh` passes (shellcheck included).

## Context
Follow-up from T-0032 (confirm-with-one-real-scripts/filer-L1.md):

Have bench.sh write its exit code and wall-clock duration to the bench log: the T-0032 verifier could not check `exit=0` or the run time because both go only to stdout.

## Constraints
bench.sh stays bash with `set -uo pipefail`, passes shellcheck, and keeps its CLI (`--bench-dir`, task args) and summary call unchanged.

## Triage
2026-09-24, user-approved: keep, P3; exit code and duration per bench task.

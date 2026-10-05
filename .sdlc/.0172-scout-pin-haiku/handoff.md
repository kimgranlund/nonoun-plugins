---
id: T-0172
title: "Pin the scout to claude-haiku-4-5"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
The Claude scout runs on a real Haiku, and the model table, rubric and checks say so.

## Context
User decision, 2026-09-30: pin the scout to `claude-haiku-4-5`. Found while checking the Claude model table against the maintainer's Max login (Claude Code 2.1.285): `claude -p --model haiku` reported `modelUsage` `claude-sonnet-5-5`, so the `haiku` alias resolves to Sonnet 5.5 there; `--model claude-haiku-4-5` resolved to `claude-haiku-4-5`, and `--model claude-haiku-5-5` failed with `unrecognized_model`. The scout configured as cheap Haiku therefore runs on Sonnet. Evidence to add: a dated note in `docs/reports/` with the probe commands and outputs.

Change, `plugins/sdlc-lite/scripts/run.sh`: the `scout:L1)` row becomes `model=claude-haiku-4-5; effort=low`. Check every place that parses or compares the model name, because a hyphenated id with digits breaks patterns like `model=[a-z]*`: `scripts/check.py` (run.sh table against the level rubric), the result header regex in `run.sh`, `scripts/order.py`, `scripts/traces/` cost and model detectors, and `scripts/run-selftest.sh`. Update `skills/level-rubric/SKILL.md` line 86 (the scout row) to name the pinned id. The Agent-tool seat ladder in the same file (line 97, `haiku` for mechanical spawns) cannot pin an id because the Agent tool takes an alias; add a sentence that `haiku` there resolves to Sonnet 5.5 on the maintainer's login.

Not in this ticket: the Codex scout (`gpt-5.6-terra` low), the `haiku` default of `scripts/hook-live-probe.sh` (a test helper), and any other role.

## Constraints
Only the scout row changes model. Add a `check.py` guard that fails when the `scout:L1` row and the rubric disagree, with a negative control. Run `codex_roles.py generate --check` and the full `check.sh`. Live check: one scout run through `run.sh` whose `modelUsage` shows `claude-haiku-4-5`.

## Closed

2026-09-30: fixed in session by /fix: scout:L1 pins claude-haiku-4-5, check.py and the rubric follow, live scout run shows claude-haiku-4-5

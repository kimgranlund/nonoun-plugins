---
id: T-0185
title: "evals/ folder, evals.py, and a model-table change must cite an eval"
type: feature
status: done
size: M
priority: P2
depends: []
created: 2026-10-01
---

## Goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

## Intent
- Do: add `.sdlc/evals/` with `AGENTS.md` (and `CLAUDE.md`) documenting the file format and procedures, one baseline eval file, and `plugins/sdlc-lite/scripts/evals.py` with `add`, `list`, and `check`. An eval file is `.sdlc/evals/<NNNN>-<slug>.md` with front matter `role`, `level`, `model`, `effort`, `host` (`claude` or `codex`), `task_set` (a short name or a path), `pass_rate` (`<passed>/<total>`), `cost_usd` (a number or `unknown`), `date` (`YYYY-MM-DD`), `evidence` (a repo path or a URL that exists), and a body with `## Method` and `## Result`. `evals.py add` writes the next number and refuses a missing field; `list` prints one line per eval; `check` validates every eval file and the lock below. The lock: `.sdlc/evals/table-lock.json` holds `table_sha256` (a hash of the Claude model rows in `plugins/sdlc-lite/scripts/run.sh` plus `plugins/sdlc-lite/adapters/codex/models.json`) and `eval` (the path of a valid eval file). `check.py` gets a guard (calling `evals.py check`) that fails when the current table hash differs from the lock, when the lock names no valid eval, or when the cited eval's `date` is not later than the lock's previous value (a changed table needs a new eval, not a reused one; the lock stores `previous_eval` for this).
- Baseline: create `0000-baseline.md` recording that the current table is the pre-eval baseline decided by the dated records `docs/reports/haiku-alias-2026-09-30.md`, `docs/reports/planner-l3-opus-2026-09-30.md`, and `docs/reports/codex-account-models-2026-09-30.md` (cite them as evidence; `pass_rate: 0/0`, `cost_usd: unknown`), and write the lock for it.
- Non-goals: changing any model or effort default, running any experiment, or deciding any allocation.
- Done when: the selftest, negative controls, and common checks pass, and `git diff` shows no change to the model rows of `run.sh` or to `models.json`.

## Context
Authoritative sources: Claude role models and efforts in `plugins/sdlc-lite/scripts/run.sh` (the `case "$role:$level"` rows), Codex in `plugins/sdlc-lite/adapters/codex/models.json` (`AGENTS.md` at the repository root lists them). The level rubric is checked against them by `check.py`. The hash must be stable: define the canonical text (the sorted `role:level model effort` rows parsed from `run.sh`, and the JSON of `models.json` with sorted keys) in `evals.py` and document it in the folder's `AGENTS.md`.

Selftest (`evals.py selftest`, wired into `check.sh`): `add` then `list` then `check` pass on a temp project; each missing or malformed field is refused with its name; a stale lock (a temp copy of `run.sh` with one model row changed) makes `check` fail naming the table; updating the lock without an eval fails; updating it with an eval path that does not exist fails; updating it with a valid new eval passes. Negative control: a patched copy of `evals.py` that skips the hash comparison makes the stale-lock case pass, which the selftest asserts it must not. Live proof (`docs/reports/evals-live-run.md`): in a throwaway copy of the repository, change one model row and show `check.py` fails; add an eval and update the lock and show it passes; revert.

## Constraints
No model default changes, ever, in this ticket. The lock and the eval files are tracked. `evals.py` reads the tables and never writes them.

## Common rules
Rules for this ticket, from the user (2026-10-01): every folder this ticket adds is self-describing through its own `AGENTS.md` (with a `CLAUDE.md` containing `@AGENTS.md`), so a role that reads one file learns the system and no skill is added; progressive disclosure holds (a short router line in `.sdlc/AGENTS.md`, details in the folder); every status or state transition is covered by a selftest case that asserts the folder or file state and the stamped fields, plus a negative control that fails when the rule is removed; a live run proves the behavior with a negative control and is recorded in a dated `docs/reports/<name>.md` (environment, exact commands, evidence, limits; an arm that cannot run is recorded unverified, never replaced by a fixture); checks to run before merging locally: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, and every selftest; update `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` layout list, and `plugins/sdlc-lite/AGENTS.md` when behavior or layout changes; do not bump versions, tag, push, or publish; generated Codex agent TOML is never edited by hand; no em dashes anywhere.

## Closed

2026-10-04: built and verified by /chain (6 steps), branch L3 verifier failed once on a doc ref and passed after the fix, merged into main in 6658615

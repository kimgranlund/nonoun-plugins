---
id: T-0690
title: "dispatch.py status finds attempts in step folders and the records dir"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py status <dir>` never prints an empty result silently: it lists the attempts in the dir's `step-*/` records too, and says where to look when there are none.

## Intent
- Do:
  1. In `status` (`plugins/sdlc-lite/scripts/dispatch.py`, line 918): after the dir's own `*.attempt.json`, also list each `step-*/*.attempt.json` under it, with the stem prefixed `step-<n>/`.
  2. When no attempt is found and `--orphans` is not set, print one line `no attempts in <dir>` and, when `order.records_dir(<dir>)` differs from the dir, append `; try <records dir>`.
- Non-goals: changing `recover` or `handoff_records`; recursing deeper than `step-*/`.
- Done when: the criteria pass.

## Context
Source: GitHub issue #40, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- 1 of 2 peer calls of `dispatch.py status <task root dir>` printed nothing.
- Partly fixed on main (8624f984): the CLI already maps a dir that holds `handoff.md`, or a `step-<n>` dir, to its records dir before calling `status` (`handoff_records`, dispatch.py:795, since T-0540 in 0.23.0; wired at dispatch.py:2078). `python3 plugins/sdlc-lite/scripts/dispatch.py status docs/work/.0675-followup-path-slug-dup` prints `verifier-L2 completed ...` on main. Still open: `status()` itself globs only `<dir>/*.attempt.json` (dispatch.py:922), so a task's step attempts at `<records dir>/step-<n>/` are not listed from the task folder, and a dir with no attempts (for example `docs/work`) prints an empty line with exit 0.
- Records dir rules: `plugins/sdlc-lite/scripts/order.py` docstring lines 20-27 (`step-<n>` records live at `records_dir(task)/step-<n>`).

## Constraints
Output lines for attempts in the dir itself are unchanged; exit code stays 0.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases: (a) status on a task folder whose only attempt sits in `step-1/` of its records dir prints a line starting `step-1/`; (b) status on a dir with no attempts prints a line starting `no attempts in`. Both cases fail with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py status docs/work/.0675-followup-path-slug-dup` still prints a `verifier-L2 completed` line.
3. `git diff --check <base sha>` exits 0.

## Outcome
`dispatch.py status` now lists `step-*/*.attempt.json` under the dir with the stem prefixed `step-<n>/` (report and delivery files resolved beside each attempt), and prints `no attempts in <dir>` plus `; try <records dir>` when that differs, unless `--orphans` is set. Two selftest cases (step-1 listing, empty-dir line) plus a `--orphans` negative control; both new cases FAIL with the status hunk reverted (red run saved), and the full dispatch selftest passes with the change.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/dispatch.py status docs/work/.0675-followup-path-slug-dup` run from the main checkout prints `verifier-L2 completed verifier-L2 parent_pid=3218`, exit 0 (the lane tree has no runtime records, so there it prints the new `no attempts in ...` line)
- `git diff --check af79c749` exit 0; `check.py` and `check-packaging.py` pass

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: af79c749f730
- Changed: see commits
- Commits: 3828935 T-0690: dispatch.py status lists step-* attempts and says where to look when empty
- Check: 1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases (a) step-1/ line ...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/dispatch.py status docs/work/.0675-followup-path-slug-dup` sti...: pass
- Check: 3 `git diff --check <base sha>` exits 0: pass
- Follow-up: note: plugins/sdlc-lite/scripts/board.py:249 now also receives orphaned... -> notes.md
- Follow-up: note: no builder-.md report was in the artifacts dir; the handoff Outcome... -> notes.md

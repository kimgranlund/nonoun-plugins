---
id: T-0774
title: "dispatch.py record tries the transcript before stdin and never blocks"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #82 reports no longer happens (title: dispatch.py record tries the transcript before stdin and never blocks).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/dispatch.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #82 (quoted):

> **Observed:** `dispatch.py record --agent-id <id> <dispatch>` from a non-interactive tool call hung until `</dev/null` was added.
>
> **Root cause:** `record` reads stdin when the result file at the dispatch's result path is missing or empty (`scripts/dispatch.py:1800-1803`), and `read_stdin` (`dispatch.py:2337`) blocks on an open non-tty pipe; the transcript fallback is only tried after stdin. Likely trigger: the result written somewhere other than the exact result path (compare #55). Not #36 or #63.
>
> **Proposed fix:** read stdin only when explicitly requested (`-` or a flag) and try the transcript before stdin.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Reproduced on main: `record --agent-id ag-solo <dispatch>` with stdin an open pipe that never closes hung in `read_stdin` (`sys.stdin.read()`) before the transcript was tried. Fix in `plugins/sdlc-lite/scripts/dispatch.py`: `read_stdin` now never blocks (a tty, a closed stdin, or a pipe with no data or EOF within `STDIN_WAIT_S` = 1s reads as empty; once bytes arrive, each further chunk waits a fifth of that). Piped final messages and error text still work, so the documented flow (conductor.md, skills: nothing on stdin, stdin only for a role with no transcript) needed no change; the record docstring and `docs/references/sdlc-internals.md` now state the no-block rule. Two selftest cases (open empty pipe records the transcript; error text on an open pipe still fails with the limit marker) are bounded by a 20s kill.
Negative control (old `read_stdin` restored): `FAIL: T-0774 record --agent-id with an open empty stdin pipe does not hang and records the transcript` and `FAIL: T-0774 record reads error text from an open stdin pipe that never closes: exit 1 and the limit marker`; selftest exit 1. With the fix: `dispatch selftest: PASS`, exit 0.
Checks: `gate_lock.py run ... dispatch.py selftest` exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 73aefc974fea2655331a98580390ed4a32d5b959` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 73aefc974fea
- Changed: see commits
- Commits: 534fd72 T-0774: dispatch.py record never blocks on stdin
- Check: 1 A `dispatch.py` selftest case reproduces the issue's report and passes; with the change reverted ...: pass
- Check: 2 gate_lock selftest exits 0, `check.py` exits 0, `check-packaging.py` passes, `git diff --check <b...: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:2397 After the first bytes... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py:4317 The new selftest cases... -> notes.md

---
id: T-0774
title: "dispatch.py record tries the transcript before stdin and never blocks"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
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

---
id: T-0767
title: "tickets.py close keeps no absolute path outside the repo"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #75 reports no longer happens (title: tickets.py close keeps no absolute path outside the repo).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/tickets.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #75 (quoted):

> **Observed:** a verifier's `## Notes` named files in a sibling workspace by absolute path (`<home>/Projects/<sibling>/...`). `tickets.py close` copied them verbatim into the notes file and the closed handoff, and the repo's absolute-path standard then failed the next gate. Fixed by hand.
>
> **Root cause:** `relative_paths` (`scripts/tickets.py:3345`) only rewrites paths under the repo toplevel or the lanes root; a sibling workspace passes through. `abs_path_warnings` (`tickets.py:1850`) only warns and never scans closed handoffs. Gap in #22 (T-0662/T-0686).
>
> **Proposed fix:** rewrite any home-directory path outside the repo relative to the repo (e.g. `../<sibling>/...`) or refuse it, and scan the closed handoff plus the notes block close writes.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `tickets.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome

Reproduced on main: close copied a sibling-workspace and a home-directory path into notes.md verbatim and never looked at the closed handoff. `relative_paths` now also writes any path under the home directory or the repo's parent directory as `../<sibling>/...` (`_outside_paths`, relative to the main checkout), keeping the in-repo and lanes-root rewrites; `path_bases` returns that reference as a third element and fanout's use is unchanged. close prints the `absolute path in a tracked work record` warning for each line of the handoff it just closed that still holds one. Selftest cases `(T-0767)` fixtures use temp dirs and a temp HOME. Negative control with both changes reverted: both new cases fail (`FAIL, these did not bite: (T-0767) close writes a sibling workspace ...` and `(T-0767) close warns on an absolute path left in the closed handoff`). `tickets.py selftest`, `fanout.py selftest`, `check.py`, `check-packaging.py` exit 0; `git diff --check` clean.

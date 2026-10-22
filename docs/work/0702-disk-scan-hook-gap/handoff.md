---
id: T-0702
title: "Lane agents ran find / for hours despite block-disk-scan"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane role can never start a whole-disk search, and its brief says to search only inside its Tree and Artifacts dir.

## Intent
- Do: find why `plugins/sdlc-lite/hooks/block-disk-scan.sh` did not stop `find / -name docs_check.py` and `bfs / -name ui-designer-L1.md -path *ux0246*` from solo and builder sub-agents (check that `_role.sh` resolves level-variant agent types such as `sdlc-lite:solo-L1` and `sdlc-lite:builder-L2`, and that the hook is registered for sub-agents); fix the cause. Add `mdfind` with no `-onlyin` to the blocked commands. Add one line to the prompt `dispatch.py prepare` and `solo_run.py` build: search only inside Tree and the Artifacts dir.
- Non-goals: blocking searches below a project folder.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "Solo and builder agents ran `find / -name docs_check.py` and `bfs / -name ui-designer-L1.md -path *ux0246*` to locate a file. They ran from lane trees at full CPU for up to 6 hours, and `find /` survived SIGTERM." Seen from a ui-kit-neue conductor session on 0.29.0. The hook's own header says it blocks find and bfs on `/` inside a role run.

## Acceptance criteria
1. The hook's regression check (`bash plugins/sdlc-lite/scripts/check.sh` job that covers hooks, or the hook test it names) exits 0 with new cases: agent type `sdlc-lite:solo-L1` running `find / -name x` is blocked; `mdfind x` is blocked; `mdfind -onlyin . x` is allowed. Each new blocked case is observed passing (exit 0) with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and a prepared prompt holds the search-scope line.
3. The Outcome names the cause found.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.

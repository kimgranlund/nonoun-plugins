---
id: T-0596
title: "plugin_min misses solo --no-worktree runs and the installed hooks' version"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0596-t0596
worktree: ../sdlc-lite.worktrees/T-0596-t0596
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugin_min:` also guards the paths T-0593 missed: `solo_run.py run` (including `--no-worktree`), and the version of the installed plugin whose hooks run in the session, not only the scripts being executed.

## Context
From the T-0593 solo (2026-10-15).
- `solo_run.py run --no-worktree` reaches none of the gated commands, so a solo run is not checked. That is the maintainer's normal path.
- The check reads the manifest next to the running script. A conductor running the source checkout's scripts sees the checkout's version, while the session's hooks come from the installed plugin cache, which is the 2026-10-15 mismatch (0.23.1 hooks against 0.24 code).

## Intent
- Do:
  1. Gate `solo_run.py run`.
  2. Also compare against the installed plugin's version when it can be found: for Claude, the newest `~/.claude/plugins/cache/sdlc-lite/sdlc-lite/<v>/` the session uses, or `CLAUDE_PLUGIN_ROOT`'s manifest, which is what the hooks run. Refuse when either is below `plugin_min:`, and name which one.
- Non-goals: Codex install paths beyond what `CLAUDE_PLUGIN_ROOT`-style env gives.
- Done when: the criteria pass.

## Constraints
No `plugin_min:` line means no check.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0. Its new case shows `run --no-worktree` refusing with `plugin_min:` above the version; the case failed before the change.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0. Its new case sets `CLAUDE_PLUGIN_ROOT` to a fixture manifest below `plugin_min:` while the scripts' own manifest is above it, and `prepare` refuses naming the hook plugin; the case failed before the change.
3. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: Dependents checked after the change, all green with CLAUDE_PLUGIN_ROOT set to the installed 0.23.1 cache: `lanes.py selftest` (rc 0), `tickets.py selftest` (PASS), `bash plugins/sdlc-lite/scripts/run-selftest.sh` (`run selftest: PASS`). The full check.sh was not run, as instructed. | note: `redck.py deviations` printed no process deviation. The criteria carry no `(red)` tag. | note: the scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0596-verifier-L2 (holds only p.diff) could not be removed, because the rm was denied by the sandbox. The throwaway worktree under tmp/0596-verifier-L2 was removed.) · verifier: verifier-L2 (sonnet) · base: 7873caf51047
- Changed: see commits
- Commits: 0aa7ee8 T-0596: plugin_min misses solo --no-worktree runs and the installed hooks' version
- Check: 1 solo_run.py selftest exits 0, new case shows `run --no-worktree` refusing with `plugin_min:`; fai...: pass
- Check: 2 dispatch.py selftest exits 0, new case sets CLAUDE_PLUGIN_ROOT to a fixture below `plugin_min:` w...: pass
- Check: 3 `git diff --check` exits 0: pass

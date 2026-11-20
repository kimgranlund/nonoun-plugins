---
id: T-0877
title: "A session agent that calls sdlc scripts from an older cached version is told so, and refused for state-changin"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0875, T-0867, T-0868]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-20
branch: lane/T-0877-t0877
worktree: ../sdlc-lite.worktrees/T-0877-t0877
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A session agent that calls sdlc scripts from an older cached version is told so, and refused for state-changing commands, whichever script it calls.

## Intent
- Do: run the T-0808 stale check from the entry points of the remaining scripts the session agents call.
- Non-goals: changing how the host expands `${CLAUDE_PLUGIN_ROOT}` in an agent prompt; `gate_lock.py` (shared ledger, many callers; warn only if anything).
- Done when: the criteria below hold.

## Context
- #91: "the session's agent rules referenced `.../nonoun/sdlc/1.0.2/scripts/*.py` while the `/sdlc:ask` skill loaded from `.../sdlc/1.0.3/`." Expected: one version per session, "or the agent prompt resolves the script path from the active plugin version".
- `plugins/sdlc/scripts/plugin_min.py` `check_stale` (line 142, T-0808): a script run from a cache folder while a newer version folder sits beside it refuses with exit 2; `SDLC_ALLOW_STALE_PLUGIN=1` keeps the warning only; a source checkout only warns. It is called today only from `dispatch.py`, `fanout.py` and `solo_run.py`.
- Add it to `main()` of `lanes.py`, `tickets.py`, `steps.py` and `messages.py`. Read-only subcommands (`list`, `who`, `status`, `blockers`, `check`) warn only; the rest follow the existing refuse rule. Name the restart in the refusal line: "restart the session to load <new version>".
- Unverified: why the harness kept the 1.0.2 path in the agent prompt after the update. Do not build on a guess about it.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1` (this repo's checkout is not in the cache, so it only warns). Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Call `check_stale` from the four entry points with the read-only split above.
2. `plugin_min.py` has no selftest; the T-0808 cases live in the `dispatch.py` selftest (around line 5749). Add the same kind of case to the `lanes.py` and `tickets.py` selftests (copy the script into a fake cache folder 1.0.2 beside an empty 1.0.3, as that case does): a state-changing command from 1.0.2 exits 2, a read-only one warns and runs, `SDLC_ALLOW_STALE_PLUGIN=1` runs with the warning.
3. Update the T-0808 paragraph in the `plugin_min.py` docstring, the sdlc-internals entry and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/tickets.py selftest` exits 0 with the new cases, which also run `lanes.py` from a fake cache folder (replan: the lanes case lives in the tickets selftest so `lanes.py` takes one line while T-0873 edits it), and both lanes selftest shards exit 0; with the call removed from `lanes.py`, the refusal case fails (state the observed red).
- `python3 plugins/sdlc/scripts/steps.py selftest` and `python3 plugins/sdlc/scripts/messages.py selftest` exit 0.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- A source checkout never refuses.

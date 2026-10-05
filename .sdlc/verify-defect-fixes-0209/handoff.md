## Task goal
Independently verify three small defect fixes on this branch. The pre-build base is commit c4909ee; the fixes are 44ed997 (T-0258), c23fb94 (T-0261), 8ed117d (T-0263). Tickets: .sdlc/0258-fanout-close-ticket-root, .sdlc/0261-split-goal-precheck, .sdlc/0263-stale-lane-route. Each regression test must fail without its fix and pass with it.

## Step 1: Verify the three fixes
level: L3

### Do
- T-0258: fanout numbered close under `ticket_root: tickets` with `.sdlc/config` untracked (gitignored) failed with `close refused: .sdlc/NNNN-slug/handoff.md: missing or has no front matter`. The fix copies the config into the integration and lane worktrees (plugins/sdlc-lite/scripts/fanout.py). Test: the "untracked config lane" case in the fanout selftest.
- T-0261: `steps.py precheck <task dir>` plus a run.sh refusal (exit 2, before any attempt record) for planner and plan-reviewer when the task handoff has no `## Goal`. Tests: steps.py selftest "(precheck)" cases and run-selftest.sh "goal precheck".
- T-0263: `steps.py next` prints `resplit` for a blocked builder whose Notes first line starts `stale lane:`. Also changed: builder.md, chain SKILL, docs/maintenance/sdlc-internals.md, generated Codex builder agents.
To show red before, make a throwaway worktree under `$SDLC_TMP_WORKTREES` at HEAD, revert only the non-test hunks of each fix there (the fanout.py config copy block, the run.sh precheck block, the steps.py `stale lane:` branch), and run the matching selftest; say what you did.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- Each of the three regression tests goes red with its fix reverted (observed, not read).

## Builder note
The builder (Sonnet) saw red then green for each: fanout selftest printed `merged, close refused: .sdlc/0001-x/handoff.md: missing or has no front matter` before the fix; run-selftest.sh printed `goal precheck: planner on a handoff with no ## Goal exited 0, want 2`; steps selftest failed `next resplit: ...`. Treat these as unverified claims.

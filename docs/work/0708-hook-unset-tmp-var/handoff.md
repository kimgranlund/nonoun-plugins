---
id: T-0708
title: "Hooks treat an unset SDLC_TMP_WORKTREES as the fallback prefix"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`block-role-rm.sh` and `block-stray-worktree.sh` judge a `$SDLC_TMP_WORKTREES` path as the shell will run it: when the variable is unset in the hook's environment, the path is refused, not mapped to the fallback prefix.

## Intent
- Do: in `plugins/sdlc-lite/hooks/block-role-rm.sh` (about line 92) and `plugins/sdlc-lite/hooks/block-stray-worktree.sh` (`VAR`/`expand`, about line 237), substitute the prefix for `$SDLC_TMP_WORKTREES` / `${SDLC_TMP_WORKTREES}` only when that variable is set and non-empty in the hook process; otherwise refuse with a reason that says to write the literal prefix from the brief. Add hook selftest cases in `plugins/sdlc-lite/scripts/hook-selftest.sh`.
- Non-goals: brief text (T-0707), other variables.
- Done when: the criteria pass.

## Repro
As a `dispatch.py prepare` role (SDLC_TMP_WORKTREES unset), run `rm -rf "$SDLC_TMP_WORKTREES/scratch"` or `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`.

## Expected
Both are refused: the shell expands them to `/scratch` and `/base`.

## Actual
T-0707 verifier-L2 (`.sdlc/runtime/tasks/0707-brief-literal-paths/verifier-L2.md` in lane T-0707-t0707): "`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD` returned rc=0 from block-stray-worktree.sh. `rm -rf "$SDLC_TMP_WORKTREES/scratch"` got an explicit `permissionDecision: allow` from block-role-rm.sh, and the shell would run it as `rm -rf /scratch`."

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 and has cases: with SDLC_TMP_WORKTREES unset, the rm and worktree-add forms above are refused; with it set, the same forms under it still pass.
2. Negative control: with the hook changes reverted, the new "unset is refused" cases fail.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Both hooks now substitute the prefix for `$SDLC_TMP_WORKTREES` / `${SDLC_TMP_WORKTREES}` only when the variable is set and non-empty in the hook process (a `varset` flag passed from `${SDLC_TMP_WORKTREES:+1}`); unset or empty, the form is refused with "write the literal prefix from the brief". Files: `plugins/sdlc-lite/hooks/block-role-rm.sh`, `plugins/sdlc-lite/hooks/block-stray-worktree.sh`, `plugins/sdlc-lite/scripts/hook-selftest.sh` (new cases for a sub-agent: unset and empty refused for the rm and worktree-add forms, set still allowed).
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exit 0 (PASS); also via gate_lock.
- Negative control: with `hooks/` reverted to base the selftest fails with `FAIL: block-stray-worktree denies 'git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD' for a sub-agent with SDLC_TMP_WORKTREES unset: exit 0, want 2`; with only `block-role-rm.sh` reverted it fails with `FAIL: block-role-rm denies 'rm -rf $SDLC_TMP_WORKTREES/scratch' for a sub-agent with SDLC_TMP_WORKTREES unset: exit 0, want 2`. Changes restored, PASS again.
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` PASS; `git diff --check 2bbee9d44740c3e5aa8c0b006ee62b0c35460168` exit 0.
- run.sh headless roles are unaffected: run.sh exports SDLC_TMP_WORKTREES for them, so the variable form still resolves.

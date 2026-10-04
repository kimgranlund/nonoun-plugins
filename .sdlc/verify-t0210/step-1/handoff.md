## Task goal
Independently verify branch t0210 (T-0210) against main before it merges. The ticket is .sdlc/.0210-spec-gate-check/handoff.md: read its Intent and Constraints and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification, proportionate. Run every criterion plus python3 plugins/sdlc-lite/scripts/specgate.py selftest and steps.py selftest. Read the ticket Intent. Check: specgate.py check flags a (guard) span running check.sh when the plan has no 'guard timeout: <seconds>' line, a criterion span repeated verbatim across steps, and a (red) tag beside (guard) on one line; it imports steps (no second criterion parser) and is read-only; run.sh plan-reviewer on a failing plan exits 2 before any model call; steps.py split --only honors the plan-level guard timeout line. In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) drop the missing-timeout flag, (b) drop the repeated-criterion flag, (c) let run.sh plan-reviewer run on a failing plan, (d) ignore the guard timeout line in split. Replay on a failing plan and a positive plan. Fail only on a real defect or unsupported claim.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/specgate.py selftest`

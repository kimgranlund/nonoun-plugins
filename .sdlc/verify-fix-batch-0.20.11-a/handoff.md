## Task goal
Independently verify four fixes on this branch, built after base 3482207 (HEAD 0e85edb). Tickets (read each handoff.md and its acceptance criteria): .sdlc/.0294-plan-review-l4-l5-only, .sdlc/.0295-lint-name-found-heading, .sdlc/.0296-lane-refuse-m-over-20-criteria, .sdlc/.0297-planner-guard-dry-run-widen-inherit. All code is in plugins/sdlc-lite/scripts/steps.py plus text in agents, skills, and docs. Each regression test must fail without its fix and pass with it.

## Step 1: Verify the four fixes
level: L3

### Do
- Work in a throwaway worktree under $SDLC_TMP_WORKTREES at HEAD to show red: revert only the non-test hunks of each fix (review_required back to the old rule for 0294; the near-heading hint in read_goal for 0295; the ticket_criteria check in lane_action for 0296; the inherit_widened call in split for 0297), run `steps.py selftest`, and say what you did. Do not edit the real tree.
- Check 0294 also: no model or effort value changed (diff run.sh rows, adapters/codex/models.json, level-rubric model table vs base 3482207), and skills/chain, agents/conductor.md, docs/lean-sdlc/design.md, skills/level-rubric state plan review is for L4 and L5 only.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- Each of the four regression cases goes red with its fix reverted (observed, not read).

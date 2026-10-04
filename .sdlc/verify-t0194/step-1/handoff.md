## Task goal
Independently verify branch t0194 (t0194) against main before it merges. The ticket is .sdlc/- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`/handoff.md: read its Intent and Constraints, and the design docs/lean-sdlc/design.md section it cites.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion. Check the lean text against the design's Lean chain section: lean conditions, the full-chain mandatory list (planner L3, any L4 or L5 step, any merge step, any replan, a Plan review line, an unresolved: assumption), the coarse-step rule, and that the lean close-out always runs the filer; fail if the text claims a lane the code cannot compute (no steps.py lane exists yet). In a throwaway copy under $SDLC_TMP_WORKTREES inject defects and show each is caught: (a) delete the Lean chain heading from chain/SKILL.md, (b) delete the independently verifiable outcome phrase from planner.md, (c) make steps lint refuse instead of warn, (d) make steps lint warn on a plan that is not lean-eligible (a Merge step, or an L4 step). Run steps.py selftest and confirm case (r) is green. Confirm the regenerated Codex planner agents match generate --check.

### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`

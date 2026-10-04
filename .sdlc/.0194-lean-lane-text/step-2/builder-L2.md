<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: new `## Coarse steps` section, placed between "Each step must be buildable" and `## Criteria that can pass`.
- plugins/sdlc-lite/skills/chain/SKILL.md: new unnumbered `## Lean chain` section, placed before `## 1. Brief`. It covers the lean conditions, the mandatory full-chain triggers, a link to the planner's Coarse steps rule, "always runs the filer" for close-out, and a note that no script computes the lane yet.
- plugins/sdlc-lite/scripts/check.py: docstring item 13 and a `LEAN_LANE` guard after the Read-first guard. Each phrase/file pair has its own negative control.
- plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1.toml, sdlc-planner-l2.toml, sdlc-planner-l3.toml: regenerated with `codex_roles.py generate`.

## Checks
All 12 acceptance criteria were run with SDLC_BASE_SHA=de46ba67, and each one passed:
- The `## Lean chain`, `always runs the filer` and `Coarse steps` greps on chain SKILL.md: PASS
- The `## Coarse steps`, `independently verifiable outcome` and `steps lint: warning:` greps on planner.md: PASS
- The grep on sdlc-planner-l2.toml: PASS
- Negative control with the planner phrase removed: check.py exits nonzero, PASS
- Negative control with `## Lean chain` removed: check.py exits nonzero, PASS
- The em dash guard: PASS
- The scope guard: PASS
- `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. shellcheck is not installed, so that check was skipped.
- `python3 scripts/check-packaging.py`: PASS
- `codex_roles.py generate --check`: PASS
- `tickets.py --root .sdlc check`: PASS
- `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: PASS
- I also ran `python3 plugins/sdlc-lite/scripts/check.py` on its own, and it passed.

## Notes
Step 1's `steps lint: warning:` text in steps.py was already in the base commit, so steps.py has no changes from this step. Nothing was committed.

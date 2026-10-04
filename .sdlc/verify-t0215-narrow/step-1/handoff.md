## Task goal
Narrow re-verification of T-0215 after the fix step. The L3 branch verifier failed on stale lane documentation only (`.sdlc/verify-t0215/step-1/verifier-L3.md`, section For the next attempt); everything else it passed. Check only what failed.

## Step 1: Verify the lane documentation fix
level: L2

### Do
Read-only. Read the finding in `.sdlc/verify-t0215/step-1/verifier-L3.md` and check each named place is now consistent with `steps.py lane` printing `solo` for size S and M before planning and `lean` or `full` after: plugins/sdlc-lite/skills/sdlc-lite/SKILL.md (Codex entry skill has a route for `solo` naming the sdlc-solo agents), plugins/sdlc-lite/skills/chain/SKILL.md (says lane prints solo, lean, or full; still holds `## Lean chain` and `always runs the filer`), docs/lean-sdlc/design.md (the two lines say solo, not fix), plugins/sdlc-lite/skills/level-rubric/SKILL.md (names solo). Run the lane output check for sizes S, M and L. Fail only if one of those places is still stale or a gate is red.

### Acceptance criteria
- `d=$(mktemp -d) && printf -- '---\nid: T-9999\nsize: M\n---\n' > $d/handoff.md && python3 plugins/sdlc-lite/scripts/steps.py lane $d | head -1 | grep -qx solo`
- `d=$(mktemp -d) && printf -- '---\nid: T-9999\nsize: S\n---\n' > $d/handoff.md && python3 plugins/sdlc-lite/scripts/steps.py lane $d | head -1 | grep -qx solo`
- `d=$(mktemp -d) && printf -- '---\nid: T-9999\nsize: L\n---\n' > $d/handoff.md && python3 plugins/sdlc-lite/scripts/steps.py lane $d | head -1 | grep -qx full`
- `grep -q "sdlc-solo-l2" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -q "## Lean chain" plugins/sdlc-lite/skills/chain/SKILL.md`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `bash plugins/sdlc-lite/scripts/check.sh`

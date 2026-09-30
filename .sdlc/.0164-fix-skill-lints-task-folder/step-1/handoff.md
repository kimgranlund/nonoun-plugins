## Task goal
The lint command that `/fix` tells the conductor to run passes for a well-formed handwritten step handoff, and a test that failed before the fix passes after it.

## Step 1: Lint the step handoff in /fix, and guard it in check.py
level: L2

### Do
In `plugins/sdlc-lite/skills/fix/SKILL.md` step 2, change the lint command from `steps.py lint .sdlc/<slug>` to `steps.py lint .sdlc/<slug>/step-1/handoff.md`, matching how `skills/chain/SKILL.md` section 5 step 3 lints its handwritten step. Add a contract check to `plugins/sdlc-lite/scripts/check.py` that fails when `skills/fix/SKILL.md` gives a `steps.py lint` command whose target is not a `step-1/handoff.md` path. Confirm the new check fails against the old text (for example on a temporary copy), then passes. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` if the check reports generated agents out of date. Background: `steps.py lint .sdlc/<task>` needs a planner file, which /fix never writes, so the documented command exits 1 with "no planner-*.md".

### Acceptance criteria
- `grep -qE 'steps\.py lint \.sdlc/.slug./step-1/handoff\.md' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -q 'step-1/handoff.md' plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`

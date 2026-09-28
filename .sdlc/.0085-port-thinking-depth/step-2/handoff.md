## Task goal
When the same finding recurs, the chain asks whether the plan or rule is wrong before retrying.

## Step 2: Guard the rule's presence in check.py
level: L2
### Do
In `plugins/sdlc-lite/scripts/check.py`:
- Add a `'recurring finding'` key to `PLAN_DEFECT_DOCS`, covering `agents/planner.md`, `agents/conductor.md`, `skills/chain/SKILL.md`, `skills/level-rubric/SKILL.md`, and `skills/handoff-format/SKILL.md`.
- Extend docstring item 5 to name the recurring-finding rule.
- Update the `check.sh` line in the repo-root `CLAUDE.md` Commands section, and the author agent file, if they list what check.py guards.
### Acceptance criteria
- Negative control (run from `plugins/sdlc-lite`, writes only to a temp dir): `t=$(mktemp -d) && cp -R . "$t/p" && cp ../../CLAUDE.md "$t/p/" && sed -i '' 's/recurring finding/recurring-xx/g' "$t/p/agents/conductor.md" && ! python3 scripts/check.py "$t/p" >/dev/null; rc=$?; rm -rf "$t"; test $rc -eq 0`
- `grep -q "'recurring finding'" scripts/check.py` (run from `plugins/sdlc-lite`)
- (guard) `scripts/check.sh` exits 0 (run from `plugins/sdlc-lite`)
- (guard) `git diff --quiet HEAD -- scripts/run.sh` (run from `plugins/sdlc-lite`)

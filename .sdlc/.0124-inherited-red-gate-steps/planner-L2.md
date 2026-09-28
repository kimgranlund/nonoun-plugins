<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Planner puts the project's whole-suite gate guards on one final "gates green" step instead of on every step, so red inherited from earlier steps or from a main sync never blocks a step whose own work is green.

## Step 1: Planner rule 14 "gates green" plus its check.py guard
level: L2
### Do
The failing check lands in this same step as the fix.
- `plugins/sdlc-lite/scripts/check.py`: add `'gates green': ('agents/planner.md',)` to `PLAN_DEFECT_DOCS`. Extend item 5 of the module docstring to name the "gates green" rule, which lives in the planner.
- `plugins/sdlc-lite/agents/planner.md`: add rule 14 under `## Criteria that can pass`, containing the literal phrase `gates green`. Proposed text:

  "14. Put the project's whole gates (the full test suite, lint, typecheck, the repo check script) as `(guard)` criteria on one final `gates green` step, never on every step. Builders never commit, so red that an earlier step or a main sync introduced lands on every later step's gate and blocks a step whose own work is green. Earlier steps check only their own behavior, with file-scoped or test-scoped commands. The final step's Do runs every gate and fixes any red the earlier steps introduced. A gate already red at the build-start HEAD comes back as builder Status `inherited red`. In a one-step plan, that step is the gates green step. A merge step keeps its own gate guards."

  Do not touch the `merge-step` block. check.py requires it to stay identical to handoff-format.
- `CLAUDE.md` (repo root): in the "A plan defect goes to a replan" decision, where the planner's rules are listed ("The planner runs each criterion once before writing it ..."), add one clause: whole-suite gate guards go on one final `gates green` step, not on every step. Mention that check.py guards the phrase.
### Acceptance criteria
- `grep -qF 'gates green' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'gates green' CLAUDE.md`
- `grep -qF "'gates green'" plugins/sdlc-lite/scripts/check.py`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite/. "$t" && cp CLAUDE.md "$t/" && sed -i '' 's/gates green//g' "$t/agents/planner.md" && python3 plugins/sdlc-lite/scripts/check.py "$t" | grep -qF 'gates green'` (negative control: check.py must flag a planner.md that lacks the phrase. Red now, because check.py prints only `ok`.)
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/skills/handoff-format/SKILL.md`

## Step 2: Gates green
level: L1
### Do
Run the repo's full gate, `bash plugins/sdlc-lite/scripts/check.sh`, on the tree with step 1's changes. Fix any red that step 1 introduced, and change only the files step 1 touched. If the gate is already red at the build-start HEAD (check it in a `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD` copy), report Status `inherited red: <tests>`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Risks
- `check.sh` took 4m51s on this host under load. That is close to the default 300s `--guard-timeout` of `steps.py split --only 2`, so run that split with `--guard-timeout 900`.
- Rule 14 lives only in the prompt. check.py proves the phrase is present, not that planners follow it. No code gate detects a full-suite guard on a non-final step, because a "whole gate" command is project-specific.
- The check.py negative control uses macOS `sed -i ''`. On GNU sed that criterion would fail to run.

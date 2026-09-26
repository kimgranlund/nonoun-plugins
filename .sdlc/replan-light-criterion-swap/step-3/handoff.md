## Task goal
Plan defects stop fewer lanes.

## Step 3: Planner rules: a guard seen red first, membership checks on files other lanes change
level: L2
### Do
- `plugins/sdlc-lite/agents/planner.md`, under `## Criteria that can pass`, append rules 11 and 12 after rule 10, with no renumbering; rules 1 to 10 keep their text.
  - Rule 11: a `(guard)` is a check that can go red. Before writing one, within rule 1's read-only limits, see it red: run its un-negated form, or run it on a fixture or in a `git worktree add <tmp> HEAD` copy where the property is absent, and keep in the criterion the exact command shape that went red (the same flags and the same output form: `vitest list` without `--filesOnly` prints test names, not file paths, so a path grep on it never matches; a cold-cache check that moves the wrong cache dir aside never runs cold). A guard, or a new-behavior criterion, whose red state cannot be observed on this host (a cold cache, a CI-only failure) is not a criterion: check the configuration or structure the step changes instead, and say in the Do that the runtime behavior is not proven by this step.
  - Rule 12: a file other lanes also change (a generated index, a registry, a catalog, a shared config) is checked by membership or structure, never by an exact line or a whole-file comparison: `grep -qF` for the entry this step adds, or a parse that finds the key, so a main sync that extends the line or the file keeps the criterion green. An exact `children: [...]` line that main later extended stopped a lane.
  - The text must hold the phrases `can go red` and `membership or structure`.
- `plugins/sdlc-lite/scripts/check.py`: add `'can go red': ('agents/planner.md',)` and `'membership or structure': ('agents/planner.md',)` to `PLAN_DEFECT_DOCS`, and name them in the docstring's item 5.
- `CLAUDE.md`, the Decisions bullet on plan defects: extend the sentence "The planner runs each criterion once before writing it (...)" so it also says the planner sees each `(guard)` red first (un-negated, or on a fixture) and checks files other lanes change by membership or structure.
### Acceptance criteria
- `grep -q "can go red" plugins/sdlc-lite/agents/planner.md`
- `grep -q "membership or structure" plugins/sdlc-lite/agents/planner.md`
- `grep -q "membership or structure" CLAUDE.md`
- `grep -q "can go red" plugins/sdlc-lite/scripts/check.py`
- `grep -q "membership or structure" plugins/sdlc-lite/scripts/check.py`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && cp CLAUDE.md "$t/p/CLAUDE.md" && perl -pi -e "s/can go red/xx/g" "$t/p/agents/planner.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" 2>&1 | grep -q "agents/planner.md: plan-defect route missing \"can go red\""` (run from the repo root; proves the guard bites)
- `test "$(sed -n "/^## Criteria that can pass/,/^## Merge steps/p" plugins/sdlc-lite/agents/planner.md | grep -cE "^1[12]\. ")" -eq 2` (rules 11 and 12 exist)
- (guard) `sed -n "/^## Criteria that can pass/,/^## Merge steps/p" plugins/sdlc-lite/agents/planner.md | grep -qE "^10\. "` (rule 10 keeps its number)
- Observable: the rules under `## Criteria that can pass` are numbered 1 to 12 with no gaps, and rules 9 and 10 read as they do at HEAD.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` (the whole-tree gate, run once at the end; 2 min 16 s here against the 300 s guard timeout, no model call)

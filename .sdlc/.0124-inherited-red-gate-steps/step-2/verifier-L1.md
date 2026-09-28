<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it on the built tree and it exited 0. The tail of its output was `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`. It can go red: `plugins/sdlc-lite/scripts/check.sh:11` runs `python3 "$root/scripts/check.py" "$root" || fail=1` and ends with `exit $fail`, and check.py went red on the fixture described in the next criterion.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: I ran it on the built tree. It exited 0 and printed `ok: 18 role levels, 8 agents checked`. Red control: I copied the plugin to a mktemp dir, removed `gates green` from `agents/planner.md` with sed, and ran check.py on the copy. It exited 1 and printed `FAIL agents/planner.md: plan-defect route missing "gates green"` and `FAIL: 18 role levels, 8 agents checked`. So the guard bites on the rule this task adds. I then removed the temp dir.

## Out of scope changes
None. `git diff --stat` shows three files: `CLAUDE.md`, `plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/scripts/check.py`. Step 1's Do names exactly these three. This step's builder reported `## Changes: None`, and the diff has no edits beyond step 1's. I read the diff: it adds rule 14 to planner.md, adds the `'gates green'` entry and its docstring line to check.py, and adds one clause to CLAUDE.md. The untracked files are only `.sdlc/0124-inherited-red-gate-steps/` run artifacts. The Do's inherited-red base check was not needed, because both gates are green on the built tree. Steelman check on that point: the Do asks for the base check only when a gate is red, so a missing base check is not a finding.

## For the next attempt
None

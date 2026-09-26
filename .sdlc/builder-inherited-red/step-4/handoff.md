## Task goal
A gate that main already made red is reported as inherited, not as a build failure or a plan defect.

## Step 4: Builder procedure, chain and conductor routing, repo docs, and a check.py guard
level: L3
### Do
- **`plugins/sdlc-lite/agents/builder.md`:**
  - Add a numbered rule for the pre-build check. Before claiming that a gate criterion failed (a check meant to hold before and after the step, such as a `(guard)` or a suite or lint over the repo, not a criterion for the step's new behavior, which is red at base by design), run the same command at the committed HEAD the build started from. Use a throwaway worktree, `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`; on a merge step use `HEAD^1` once the merge commit exists. This leaves the step's own changes untouched.
  - If the gate is red there with the same failures (the same failing test names or findings), Status is `inherited red: <tests>`, listing the failing tests. Notes give both runs' commands and outcomes, and the work done so far stays in the tree.
  - If the failures differ, or the gate is green at base, it is an ordinary failure.
  - Remove "or fails on findings that predate this build and that the step does not ask to fix" from the `plan defect:` sentence. `plan defect` keeps parse errors, contradictions, and criteria that are wrong on their face.
  - Change the Status line of the output format to `done | blocked | inherited red: <tests>`.
- **`plugins/sdlc-lite/skills/chain/SKILL.md`:**
  - In the step 4 action list, add `inherited` → the gate was already red at the pre-build HEAD (Status `inherited red: <tests>`). Interactive: ask the user through AskUserQuestion (fix main first, rebuild once main is green, or stop). Unattended: stop the task and report the inherited tests. It is never a fail, a rebuild, a bump, or a replan, and never waives the gate.
  - Add a numbered item 7 under "For each step" that says the same.
- **`plugins/sdlc-lite/agents/conductor.md`:** add the same `inherited red` routing to the escalation bullet in "How you run roles".
- **`CLAUDE.md` (repo root):**
  - In the `scripts/steps.py` bullet, change the action list to `(`build`, `verify`, `reverify`, `rebuild`, `bump`, `replan`, `done`, `stop`, `inherited`)`. Add that a builder Status `inherited red: <tests>` maps to `inherited`.
  - Add a clause that `board.py` renders an inherited red step 🔴 and `run.sh` accepts that Status.
- **`.claude/agents/sdlc-lite-author.md`:** add an "Inherited-red route" invariant line, modeled on the No-verdict route line. It names steps.py, board.py, run.sh, builder.md, chain SKILL.md, conductor.md, check.py, and CLAUDE.md as the places that must stay in sync.
- **`plugins/sdlc-lite/scripts/check.py`:**
  - Add a guard in the pattern of `PLAN_DEFECT_DOCS`: the phrase `inherited red` must appear in `agents/builder.md`, `agents/conductor.md`, `skills/chain/SKILL.md`, `scripts/steps.py`, `scripts/board.py`, and `scripts/run.sh`.
  - Each miss appends the error `<rel>: inherited-red route missing "inherited red"`.
  - Add a numbered item for it to the module docstring.
### Acceptance criteria
- `grep -q 'inherited red: <tests>' plugins/sdlc-lite/agents/builder.md`
- `! grep -q 'findings that predate this build' plugins/sdlc-lite/agents/builder.md`
- `grep -q 'inherited red' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q 'inherited red' plugins/sdlc-lite/agents/conductor.md`
- `grep -q "replan., .done., .stop., .inherited" CLAUDE.md`
- `grep -q 'inherited red' .claude/agents/sdlc-lite-author.md`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && cp CLAUDE.md "$t/p/CLAUDE.md" && perl -pi -e 's/inherited red/xx/g' "$t/p/agents/conductor.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" 2>&1 | grep -q 'agents/conductor.md: inherited-red route missing "inherited red"'` (run from the repo root; proves the new guard bites)
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

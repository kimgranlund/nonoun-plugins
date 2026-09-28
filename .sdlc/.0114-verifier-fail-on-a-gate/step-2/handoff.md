## Task goal
A gate that is already red at the pre-build HEAD is reported as inherited whether the builder or the verifier finds it, so it never costs a rebuild, a level bump, or a replan.

## Step 2: Verifier procedure, routing docs, and check.py guard
level: L2
### Do
- `plugins/sdlc-lite/agents/verifier.md`:
  - Add the pre-build gate check. A gate criterion is a check meant to hold before and after the step, such as a `(guard)` or a repo-wide suite or lint. It is never a criterion for the step's new behavior.
  - Before failing a gate criterion, the verifier runs the same command at the pre-build HEAD in a throwaway worktree under `$SDLC_TMP_WORKTREES`, without changing git state. The pre-build HEAD is the commit the builder started from: HEAD when the builder made no commit, `HEAD^1` for a merge step.
  - Red there with the same failures gives the Verdict `inherited red: <tests>`, listing the failing tests, with both runs as evidence. Green there, or different failures, gives an ordinary `fail`.
  - If any non-gate criterion also fails, the verdict is `fail`. `inherited red` applies only when every failing criterion is an inherited gate.
  - Remove "fails only on findings that predate the build" from the `plan defect:` sentence. `plan defect` keeps: does not parse, contradicts another criterion, vacuous.
  - Change the Verdict format line to exactly `pass | fail | inherited red: <tests>`, and state that a bare `inherited red` with no colon is no verdict.
- `plugins/sdlc-lite/skills/chain/SKILL.md` step 4: extend the `inherited` action text and rule 7 to cover the verifier. Use the literal phrase "verifier Verdict `inherited red: <tests>`" on the same line as the routing. The routing is the same as the builder case: interactive ask, unattended stop; never a fail, rebuild, bump, replan, or reverify.
- `plugins/sdlc-lite/agents/conductor.md` line 23: add the same phrase and routing.
- Repo-root `CLAUDE.md`:
  - In the `steps.py` bullet, add that a verifier Verdict `inherited red: <tests>` maps to `inherited`, next to the builder Status clause.
  - In the `run.sh` bullet, add that run.sh accepts that Verdict.
- `.claude/agents/sdlc-lite-author.md` Inherited-red route bullet: add that a verifier Verdict `inherited red: <tests>` (found by the verifier's pre-build gate check) routes the same way, and add verifier.md to the sync list.
- `skills/handoff-format/SKILL.md` currently lists no Verdict values. Change it only if it does.
- `plugins/sdlc-lite/scripts/check.py`: add `'agents/verifier.md'` to `INHERITED_RED_DOCS`, and update docstring item 8 to name verifier.md.
### Acceptance criteria
- `grep -qxF 'pass | fail | inherited red: <tests>' plugins/sdlc-lite/agents/verifier.md`
- `grep -q 'pre-build HEAD' plugins/sdlc-lite/agents/verifier.md`
- `! grep 'plan defect' plugins/sdlc-lite/agents/verifier.md | grep -q predate`
- `grep -i 'verifier verdict' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q 'inherited red'`
- `grep -i 'verifier verdict' plugins/sdlc-lite/agents/conductor.md | grep -q 'inherited red'`
- `grep -i 'verifier verdict' CLAUDE.md | grep -q 'inherited red'`
- `grep -i 'verifier verdict' .claude/agents/sdlc-lite-author.md | grep -q 'inherited red'`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && cp CLAUDE.md "$t/p/" && perl -pi -e 's/inherited red/INHERITED/g' "$t/p/agents/verifier.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" | grep -q 'agents/verifier.md: inherited-red'`
- (guard) `plugins/sdlc-lite/scripts/check.sh`

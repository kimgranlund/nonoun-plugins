<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
When a verifier finds that a gate was already red at the pre-build HEAD, it reports the verdict `inherited red: <tests>`. That verdict routes to `inherited` in `steps.py next`, shows as 🔴 inherited red on the board, and is accepted by run.sh. It never costs a rebuild, a level bump, a replan, or a reverify. `pass`, `fail`, and the builder's inherited-red path keep their current behavior.

## Step 1: Route, render, and accept the verifier `inherited red:` verdict in the scripts
level: L3
### Do
- `plugins/sdlc-lite/scripts/steps.py`:
  - `verdict_or_none` (and anything it feeds) returns `'inherited'` when the first non-blank line under `## Verdict` starts with `inherited red:` (any case), the same as `build_status_or_none` does for the builder.
  - A bare `inherited red` with no colon stays a no-verdict, so it routes to `reverify`.
  - In `next_action`, after the no-verdict branch and before the `pass`/`plan defect`/fail counting, a newest verifier that counts after the build and has the verdict `inherited` returns `('inherited', None, <reason naming the verifier file and "gate already red at the pre-build HEAD">, read)`.
  - An inherited verdict never counts as a fail in the counting loop and never counts as a no-verdict run. It also breaks the consecutive no-verdict count, the way a real verdict does.
  - Update the `next` rules in the module docstring with the new line.
  - Add selftest cases:
    - done builder, then verifier `inherited red: test_a`, gives `inherited`.
    - verifier with a bare `inherited red` gives `reverify L1`.
    - done, fail, rebuild, then an inherited verifier gives `inherited`, not `bump`.
    - an inherited verifier, then a rebuild and a `fail` verifier at the same level, gives `rebuild L2`, not `bump`. The inherited verdict never counts as a fail.
    - an existing `fail` still gives `rebuild L2`.
  - Selftest fixture strings use the form `'## Verdict\ninherited red: test_a\n'`.
- `plugins/sdlc-lite/scripts/board.py`:
  - In `step_row`, a newest verifier that counts after the build and whose Verdict starts with `inherited red:` renders `'🔴', 'inherited red · builder <L> · verifier <L>, ask the user<tries>'`.
  - The no-verdict counting loop treats `inherited red:` as a verdict.
  - Update the module docstring.
  - Add a selftest case with the fixture string `'## Verdict\ninherited red: test_a\n'`.
- `plugins/sdlc-lite/scripts/run.sh`:
  - Change the verifier's allowed value to `pass|fail|inherited red: .+`.
  - Update the header comment near line 18.
- `plugins/sdlc-lite/scripts/run-selftest.sh`:
  - Add `want_rc 0 verifier L1 $'## Verdict\ninherited red: test_a'`.
  - Add `want_rc 3 verifier L1 $'## Verdict\ninherited red'`.
### Acceptance criteria
- `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\ninherited red: test_a\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" >"$d.out" && test "$(head -1 "$d.out")" = inherited`
- (guard) `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\nfail\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = "rebuild L2"`
- (guard) `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\ninherited red\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = "reverify L1"`
- `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\ninherited red: test_a\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && python3 -c "import sys,pathlib; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import board; r=board.step_row(pathlib.Path(sys.argv[1]),'x','L2'); sys.exit(0 if r[0]=='🔴' and r[1].startswith('inherited red') else 1)" "$d"`
- (guard) `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\nfail\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && python3 -c "import sys,pathlib; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import board; r=board.step_row(pathlib.Path(sys.argv[1]),'x','L2'); sys.exit(0 if r[0]=='🔴' and r[1].startswith('fail') else 1)" "$d"`
- `grep -q 'Verdict\\ninherited red: ' plugins/sdlc-lite/scripts/steps.py`
- `grep -q 'Verdict\\ninherited red: ' plugins/sdlc-lite/scripts/board.py`
- `grep -q "want_rc 0 verifier L1 .*inherited red: " plugins/sdlc-lite/scripts/run-selftest.sh`
- `grep -q "want_rc 3 verifier L1 .*inherited red'$" plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`

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

## Risks
- `fanout.py` `inherited_red()` reads the tests from the newest builder's `## Status`. After a verifier-inherited step it would report `inherited red: step-<n>: done`. The lane still stops correctly and nothing merges, but the outcome text names the wrong tests. The ticket lists fanout changes as a non-goal, so this is left for a follow-up ticket.
- The steps.py and board.py fixtures write `runs.jsonl` so that order.py puts the verifier after the builder. Without it, the fallback ordering by level (L1 before L2) would put the verifier first.
- The step 2 docs criteria depend on the literal phrase "verifier Verdict" landing on the same line as `inherited red` in each doc.
- `check.sh` takes about 60s, well under the 300s guard timeout.

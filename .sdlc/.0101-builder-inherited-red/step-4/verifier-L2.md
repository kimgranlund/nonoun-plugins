<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `grep -q 'inherited red: <tests>' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: I ran it and it exited 0. The phrase is in the builder.md diff, in rule 8 and in the Status line `done | blocked | inherited red: <tests>`.
- `! grep -q 'findings that predate this build' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: exit 0. The builder.md diff shows the phrase removed from rule 3, which now ends "or is wrong on its face". The file exists, so the `!` is not vacuous.
- `grep -q 'inherited red' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: exit 0. The diff adds `inherited` to the step 4 action list and a numbered item 7 under "For each step". Both say interactive asks through AskUserQuestion (fix main first, rebuild once main is green, or stop), unattended stops and reports, and it is never a fail, rebuild, bump or replan, and never waives the gate.
- `grep -q 'inherited red' plugins/sdlc-lite/agents/conductor.md`: pass. Evidence: exit 0. The diff extends the escalation bullet in "How you run roles" with the same routing.
- `grep -q "replan., .done., .stop., .inherited" CLAUDE.md`: pass. Evidence: exit 0. The diff changes the `steps.py` action list to end with `inherited`. It adds that Status `inherited red: <tests>` maps to `inherited`, that `board.py` renders it 🔴, and that `run.sh` accepts it.
- `grep -q 'inherited red' .claude/agents/sdlc-lite-author.md`: pass. Evidence: exit 0. The "Inherited-red route" line is added and names steps.py, board.py, run.sh, builder.md, chain SKILL.md, conductor.md, check.py and CLAUDE.md.
- Guard-bite command (copy the plugin, blank `inherited red` in conductor.md, run check.py): pass. Evidence: I ran it verbatim from the repo root and it exited 0. Printing the check.py output showed `FAIL agents/conductor.md: inherited-red route missing "inherited red"`. As a negative control, an unmodified plugin copy gave 0 `inherited-red` lines from check.py. The biting variable is the `inherited red` phrase in conductor.md, and the check goes red only when it is removed. The check.py diff adds `INHERITED_RED_DOCS` over the six required files, the `<rel>: inherited-red route missing "inherited red"` error, and docstring item 8.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: `exit=0` on a direct run. The output shows the steps, order, fanout, run, hook and live-probe selftests PASS, plus `ok: shellcheck` and `ok: plugin validate`. The only "fail" text in the output is inside `ok:` lines.

## Out of scope changes
- The `git diff --stat` also lists board.py, run.sh, steps.py, run-selftest.sh and `.sdlc/0101-builder-inherited-red/handoff.md`, none of which this step names. The builder's Notes attribute them to steps 1 to 3, and the working tree is uncommitted, so I read them as earlier steps' work. I cleared them with two checks. The step 4 files in the diff are exactly the ones its Do names. The new guard requires `inherited red` in board.py, run.sh and steps.py, and check.sh passes, so those files do contain the phrase from earlier steps.

## For the next attempt
None

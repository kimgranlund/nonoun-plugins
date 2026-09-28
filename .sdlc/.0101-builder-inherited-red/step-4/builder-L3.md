<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/builder.md: added rule 8, the pre-build check. It applies to gate criteria only. It runs the same command at the committed HEAD in `$SDLC_TMP_WORKTREES/base` (or at `HEAD^1` on a merge step once the merge commit exists). Same failures there give Status `inherited red: <tests>` with both runs in Notes and the work left in the tree. Different failures, or green at base, are an ordinary failure. Removed "fails on findings that predate this build..." from the `plan defect:` sentence, which now reads "or is wrong on its face". The Status line is now `done | blocked | inherited red: <tests>`.
- plugins/sdlc-lite/skills/chain/SKILL.md: added `inherited` to the step 4 action list. Interactive asks the user through AskUserQuestion (fix main first, rebuild once main is green, or stop). Unattended stops and reports the inherited tests. It is never a fail, rebuild, bump, or replan, and never waives the gate. Added item 7 under "For each step" with the same rule.
- plugins/sdlc-lite/agents/conductor.md: added the same `inherited red` routing to the escalation bullet in "How you run roles".
- CLAUDE.md: the `steps.py` action list now ends with `inherited`. Added that builder Status `inherited red: <tests>` maps to `inherited`, that `board.py` renders the step 🔴 inherited red, and that `run.sh` accepts that Status.
- .claude/agents/sdlc-lite-author.md: added the "Inherited-red route" invariant, which names steps.py, board.py, run.sh, builder.md, chain SKILL.md, conductor.md, check.py, and CLAUDE.md.
- plugins/sdlc-lite/scripts/check.py: added the `INHERITED_RED_DOCS` guard over the six files. Each miss gives `<rel>: inherited-red route missing "inherited red"`. Added docstring item 8.

## Checks
- `grep -q 'inherited red: <tests>' plugins/sdlc-lite/agents/builder.md`: PASS
- `! grep -q 'findings that predate this build' plugins/sdlc-lite/agents/builder.md`: PASS
- `grep -q 'inherited red' plugins/sdlc-lite/skills/chain/SKILL.md`: PASS
- `grep -q 'inherited red' plugins/sdlc-lite/agents/conductor.md`: PASS
- `grep -q "replan., .done., .stop., .inherited" CLAUDE.md`: PASS
- `grep -q 'inherited red' .claude/agents/sdlc-lite-author.md`: PASS
- The guard-bite command (copy the plugin, blank `inherited red` in conductor.md, run check.py and grep for the error), run from the repo root: PASS, the new guard reports conductor.md.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, no FAIL lines. All selftests (steps, order, fanout, run, hook, live-probe), shellcheck, and plugin validate were ok.

## Notes
- The uncommitted changes to board.py, run.sh, run-selftest.sh, steps.py, and the task handoff come from earlier steps (1 to 3). This step did not touch them.
- No commit was made (this is not a merge step).

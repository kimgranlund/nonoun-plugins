<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/verifier.md: new procedure item 4 for the pre-build gate check (the pre-build HEAD is HEAD, or `HEAD^1` on a merge step). Verdict is `inherited red: <tests>` only when every failing criterion is an inherited gate. Removed "predate" from the `plan defect` sentence. The Verdict line is now `pass | fail | inherited red: <tests>`, with a note that a bare `inherited red` is no verdict.
- plugins/sdlc-lite/skills/chain/SKILL.md: the step 4 `inherited` action and rule 7 now cover a verifier Verdict `inherited red: <tests>`, and "or a reverify" is added to the never-list.
- plugins/sdlc-lite/agents/conductor.md: line 23 has the same verifier Verdict phrase and routing.
- CLAUDE.md: the steps.py bullet maps a verifier Verdict `inherited red: <tests>` to `inherited`. The run.sh bullet and the steps.py clause both say run.sh accepts that Verdict.
- .claude/agents/sdlc-lite-author.md: the Inherited-red route bullet covers the verifier Verdict, and verifier.md is added to the sync list.
- plugins/sdlc-lite/scripts/check.py: `agents/verifier.md` is added to `INHERITED_RED_DOCS`, and docstring item 8 now names it.

## Checks
- All 8 non-guard acceptance criteria were run one at a time with `bash -c`: each exited 0.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: exit 0. Every selftest passed, plus shellcheck and plugin validate.

## Notes
- skills/handoff-format/SKILL.md lists no Verdict values, so it was not changed.
- The tree already had step 1's uncommitted changes (run.sh, steps.py, board.py, run-selftest.sh), which this step builds on. run.sh already accepts the `inherited red: .+` Verdict. Nothing was committed.

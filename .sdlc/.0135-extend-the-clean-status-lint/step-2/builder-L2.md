<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/planner.md`: extended rule 13 to forbid a clean whole-tree diff. That covers `git diff --quiet` or `--exit-code` with no `-- <pathspec>` and no two-commit range, and an empty `git diff` output. `steps.py split` refuses it as a `plan defect`. The detector reads span text only, so a check hidden in a "script the span calls" is not caught and must not be written. The porcelain wording is unchanged.
- `CLAUDE.md`: in the `scripts/steps.py` bullet, next to the porcelain clause, added the clean whole-tree diff clause and the script-the-span-calls limit.
- `.claude/agents/sdlc-lite-author.md`: line 18 now reads "one that requires a clean porcelain status or a clean whole-tree diff".
- `plugins/sdlc-lite/scripts/check.py`: added `'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py'),` to `PLAN_DEFECT_DOCS`.

## Checks
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/agents/planner.md`: exit 0.
- `grep -qF 'script the span calls' plugins/sdlc-lite/agents/planner.md`: exit 0.
- `grep -qF 'clean whole-tree diff' CLAUDE.md`: exit 0.
- `grep -qF 'clean whole-tree diff' .claude/agents/sdlc-lite-author.md`: exit 0.
- `grep -qF "'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py')" plugins/sdlc-lite/scripts/check.py`: exit 0.
- (guard) `grep -qF 'clean porcelain status' plugins/sdlc-lite/agents/planner.md`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. Every selftest printed PASS, and shellcheck and `claude plugin validate` were ok.
- `grep -c '—' plugins/sdlc-lite/agents/planner.md CLAUDE.md`: exit 1, no matches, so neither file has an em dash.

## Notes
- The combined command ran past its 900s Bash timeout, so the harness moved it to the background. The slow part was the fanout selftest on a loaded host. I waited for it to finish in the foreground and read its full output, including rc=0, before reporting.
- The earlier report said the em dash check had not run. It did run: its "no matches" result arrived only in the task's completion notification. That result is listed under Checks.

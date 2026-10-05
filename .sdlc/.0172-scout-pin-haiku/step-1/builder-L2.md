<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/run.sh: `scout:L1` row now `model=claude-haiku-4-5;  effort=low ;;`.
- plugins/sdlc-lite/scripts/check.py: run.sh model pattern is now `[\w-]+`. `cap()` maps `claude-<family>-<major>-<minor>` to `<Family> <major>.<minor>` and keeps aliases as before. Both rubric cell patterns now accept an optional ` N.N` version. Added a scout pin guard (`scout_mismatch`) with a `cap()` self-check and a built-in negative control.
- plugins/sdlc-lite/skills/level-rubric/SKILL.md: scout row is now `Haiku 4.5 low`. Added the alias sentence after the `haiku` Agent-tool seat line.
- plugins/sdlc-lite/adapters/codex/agents/{sdlc-planner-l1,l2,l3, sdlc-plan-reviewer-l1, sdlc-plan-reviewer-l1-alternate}.toml: regenerated with `codex_roles.py generate`. Each file changed by one line.
- docs/reports/haiku-alias-2026-09-30.md: new dated probe note.
- docs/README.md: link to the new note, placed after the Codex tier mirror entry.

## Checks
- Criterion 1 grep on the run.sh scout row: exit 0
- Criterion 2 grep on the rubric scout row: exit 0
- Criterion 3 dry-run `run.sh scout L1` output contains `--model claude-haiku-4-5`: exit 0
- Criterion 4 grep for `claude-haiku-4-5` in the validation note: exit 0
- Criterion 5 grep for the note's link in docs/README.md: exit 0
- `python3 plugins/sdlc-lite/scripts/check.py`: `ok: 19 role levels, 9 agents checked`, exit 0
- `python3 plugins/sdlc-lite/scripts/traces.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: first run exit 2 (drift in sdlc-planner-l1.toml). At `$SDLC_BASE_SHA` in a throwaway worktree it exits 0, so this step caused the drift. After `codex_roles.py generate` it prints "Codex agent definitions verified", exit 0.
- `git diff --check`: clean

## Notes
- Step 4 needed no pattern changes, so no selftest cases were added. `traces/sources/results.py` reads the header with `(\w+)=(\S+)`, and `\S+` already accepts hyphenated ids. No detector under `scripts/traces/detectors/` and nothing in `steps.py` parses a model name. The only `model` hit in `order.py` is a comment.
- The generated Codex TOMLs changed because the planner and plan-reviewer agents preload the level-rubric skill and embed its text. They are regenerated output from the step's own rubric edit, not a change in scope.
- The guard's negative control runs inside check.py on every run, and no failure was reported. It swaps the scout model for `claude-haiku-9-9` and requires the guard to flag it. I did not separately edit a real file to watch the guard fail.

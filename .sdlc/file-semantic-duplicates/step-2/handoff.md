## Task goal
/file flags a follow-up that restates an existing open ticket, before it is filed.

## Step 2: /file step 3.2 marks likely duplicates of open tickets, with a check.py guard
level: L2
### Do
Change `plugins/sdlc-lite/skills/file/SKILL.md` in four places:
- Step 3.1: also say the dry run lists each open ticket as `open T-NNNN <title> [<slug>]`.
- Step 3.2: besides the artifact check, compare each follow-up that is not already marked `duplicate of` against those open-ticket lines. Mark one that restates an open ticket's problem in different words as `likely duplicate of T-NNNN` for dropping, with a one-line reason. Use the T-0047 case as the example: `calc.div raises an unhandled ZeroDivisionError when b == 0` versus T-0002 `div crashes on zero divisor`.
- Steps 3.3 and 3.5: leave likely duplicates out of the recommended and unattended sets, and `--skip` their indices.
- Step 3.6: report them with the matching id.

In `plugins/sdlc-lite/scripts/check.py`, add a numbered docstring item and a check that fails, naming `skills/file/SKILL.md`, when that file lacks either `likely duplicate` or `open T-NNNN`. This is the test that lands with the fix.

In `.claude/agents/sdlc-lite-author.md`, extend the "Keep `close --dry-run`/`--skip`/`--expect` and duplicate follow-up skipping in sync" sentence to cover the open-ticket listing and the /file likely-duplicate step.
### Acceptance criteria
- `grep -q "likely duplicate" plugins/sdlc-lite/skills/file/SKILL.md && grep -q "open T-NNNN" plugins/sdlc-lite/skills/file/SKILL.md`
- `t=$(mktemp -d) && mkdir -p "$t/r/plugins" && cp -R plugins/sdlc-lite "$t/r/plugins/sdlc-lite" && cp CLAUDE.md "$t/r/" && python3 plugins/sdlc-lite/scripts/check.py "$t/r/plugins/sdlc-lite" && sed -i '' 's/likely duplicate/likely dupe/g' "$t/r/plugins/sdlc-lite/skills/file/SKILL.md" && ! python3 plugins/sdlc-lite/scripts/check.py "$t/r/plugins/sdlc-lite" && python3 plugins/sdlc-lite/scripts/check.py "$t/r/plugins/sdlc-lite" | grep -q 'skills/file/SKILL.md'`
- `grep -q "likely duplicate" .claude/agents/sdlc-lite-author.md`
- Observable: in `skills/file/SKILL.md`, step 3.2 tells the session to read the dry run's `open` lines and name the matching T-NNNN, and steps 3.3, 3.5, and 3.6 all treat likely duplicates as dropped.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

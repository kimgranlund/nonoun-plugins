<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `/file` flag a follow-up that restates an open ticket in different words before it gets filed. `close --dry-run` will list the open tickets, and `/file` step 3.2 will mark likely duplicates for dropping, naming the matching id.

## Step 1: close --dry-run lists open tickets
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, `cmd_close`: when `dry_run` is set, add one line per open ticket after the numbered follow-up lines and before the optional `rename ...`, the `ack warnings: ...` line, and the final `expect <digest>` line. An open ticket is one whose status is `proposed`, `ready`, or `blocked`, excluding the ticket being closed. The line format is exactly `open <id> <full title> [<folder>]`, taken from the `ts` list already loaded, in id order. Change nothing else:
- The digest is unchanged.
- A real close's output is unchanged.
- Refusals are unchanged.
- `expect <digest>` stays the last line.

Update the selftest:
- Adjust case (p) so its index check reads only the numbered lines. That means ignoring lines that start with `open `, since beta is open in that fixture.
- Add a new case whose label contains the words `open tickets listed`. It must prove three things: a proposed or ready ticket is listed with its full title, a done or dropped ticket is not listed, and the ticket being closed is not listed.

Keep the docs in sync by stating the new `open T-NNNN <title> [<slug>]` lines in each of these:
- the module docstring's `close --dry-run` paragraph
- the `--dry-run` argparse help
- `plugins/sdlc-lite/skills/ticket/SKILL.md` item 4
- the tickets.py bullet in the repo-root `CLAUDE.md`
### Acceptance criteria
- `t=$(mktemp -d) && T=plugins/sdlc-lite/scripts/tickets.py && python3 $T --root "$t" new bug div-crash "div crashes on zero divisor" && python3 $T --root "$t" new bug old-crash "old crash" && sed -i '' 's/^status:.*/status: dropped/' "$t/old-crash/handoff.md" && python3 $T --root "$t" new feature calc Calc && printf '## Warnings\nNone\n\n## Follow-ups\n- calc.div raises an unhandled ZeroDivisionError when b == 0\n' > "$t/calc/filer-L1.md" && out=$(python3 $T --root "$t" close calc --dry-run) && test "$(printf '%s\n' "$out" | grep '^open ')" = 'open T-0001 div crashes on zero divisor [div-crash]' && printf '%s\n' "$out" | tail -1 | grep -q '^expect '`
- `grep -q "open tickets listed" plugins/sdlc-lite/scripts/tickets.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `grep -q "open T-NNNN" plugins/sdlc-lite/scripts/tickets.py && grep -q "open T-NNNN" plugins/sdlc-lite/skills/ticket/SKILL.md && grep -q "open T-NNNN" CLAUDE.md`
- Observable: if the builder's new dry-run `open` lines are commented out in a scratch copy of tickets.py, that copy's `selftest` fails on the `open tickets listed` case. Revert afterwards and do not leave the tree changed.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

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

## Risks
- Semantic matching stays a model judgment in the `/file` session, so no code can prove it catches every restated ticket. Only the data feed (step 1) and the instruction's presence (step 2) are checked mechanically.
- The open-ticket list only covers tickets under the local `--root`. An open ticket that exists only in another worktree or on an unmerged branch will not be listed.
- Something outside the /file skill might parse the dry-run output by line position. The grep found none (fanout runs a plain close), but a missed consumer would break.
- The criteria use BSD `sed -i ''`, which is macOS syntax. They assume the verifier runs on this darwin host.

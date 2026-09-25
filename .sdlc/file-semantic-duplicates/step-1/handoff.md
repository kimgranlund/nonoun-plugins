## Task goal
/file flags a follow-up that restates an existing open ticket, before it is filed.

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

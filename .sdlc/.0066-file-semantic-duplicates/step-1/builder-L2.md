<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: `close --dry-run` now prints one `open <id> <title> [<folder>]` line for each other ticket that is proposed, ready, or blocked, in id order. These lines come after the follow-up lines and before the rename, ack, and `expect` lines. The docstring and the `--dry-run` help describe them. Case (p)'s index check skips `open ` lines. New selftest case (p2) is labelled "open tickets listed".
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: item 4 describes the `open T-NNNN <title> [<slug>]` lines.
- `CLAUDE.md`: the tickets.py bullet describes the same lines.

## Checks
- Criterion 1 (div-crash / old-crash / calc scenario): passed. Exactly one `open` line, `open T-0001 div crashes on zero divisor [div-crash]`, and the last line starts with `expect `.
- `grep -q "open tickets listed" plugins/sdlc-lite/scripts/tickets.py`: passed.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- `grep -q "open T-NNNN"` in tickets.py, the ticket SKILL.md, and CLAUDE.md: all passed.
- Negative control: in a copy of the plugin in a temp dir, with the `open` lines removed from the output, the selftest failed on (p2) "open tickets listed" as intended. The working tree was not touched.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc=0.

## Notes
The negative control needs a copy of the whole plugin dir. Copying only `scripts/*.py` crashes the selftest with a FileNotFoundError on `alpha/handoff.md`.

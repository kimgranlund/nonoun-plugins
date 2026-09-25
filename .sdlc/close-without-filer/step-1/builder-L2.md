<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: `cmd_close` gains `reason=None`. The `fm`/`head` computation now happens once, before the filer lookup, and both paths share it. The reason path closes without a filer and appends a `## Closed` section. The `close` subcommand gets a `--reason TEXT` flag, and `main` passes it through `kw`. The usage docstring and help text are updated. Selftest cases (k) to (o) are added after (j).

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: `tickets selftest: PASS`.
- Negative control: I copied tickets.py to /tmp, changed `if reason is not None:` to `if False:`, and ran selftest. It reported FAIL, with misses in (k), (l), (n), and both (o) cases. I then restored the file from the copy. No git stash was used.
- Temp `.sdlc` holding alpha and beta tickets with no filer files:
  - `close alpha` gave rc=1 with "run /file on the task first".
  - `close alpha --reason "  "` gave rc=1, and `diff -r` against a copy of the tree showed nothing changed.
  - `close alpha --reason "done by T-0002"` gave rc=0. `status: done` is set, and the handoff ends with `## Closed` / `2026-09-24: done by T-0002`. `roadmap.md` shows T-0001 as done.
  - `check` printed `ok: 2 tickets, roadmap current` with rc=0.
- `scripts/check.sh`: the tail shows the steps and run selftests passing, plus shellcheck and plugin validate ok.

## Notes
- Case (m) does not fail under the negative control. With reason handling turned off, an empty reason falls through to the "no filer" refusal, which also exits 1 and writes nothing, so (m) still passes. Its assertion does not check the error text.
- The `## Closed` line is `<YYYY-MM-DD>: <reason>`, with the date written once. The handoff's `<YYYY-MM-DD> (<date.today().isoformat()>)` wording is ambiguous, and repeating the date seemed unintended.

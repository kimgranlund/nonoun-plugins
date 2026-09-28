<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: adds `--numbered` to the `close` subparser. `cmd_close` now takes `numbered=False`, OR'd with `config_numbered(root)`, and `run`/`main` pass it through. In numbered mode:
  - each follow-up's own new id is worked out once, and the folder name `NNNN-<base>` is built from it;
  - the name-clash check (`-2`, `-3`, ...) runs against that final numbered name;
  - a leading `NNNN-` is stripped from the base slug so the prefix never doubles.

  The "plan everything first" structure is unchanged. The docstring and usage lines are updated, and the selftest gains case (i): numbered close by flag and by config, a clash that appends `-2`, and a plain-mode control.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS. Existing cases (a) to (h) are unchanged and still pass. Plain close still makes bare-slug folders (`add-retry-to-fetch`, `add-retry-to-fetch-2`, `0042-fix-the-parser`).
- Proof the new case catches a bug: I made a copy of the script that forces `numbered=False` inside close's loop. Its selftest FAILED on both numbered cases, the flag one and the config one.
- `plugins/sdlc-lite/scripts/check.sh`: all ok. Role levels, both selftests, tickets, board, shellcheck and plugin validate all passed.

## Notes
- `git diff` also shows Step 1's uncommitted changes to `tickets.py` and to the task `handoff.md`. I did not touch the handoff.
- In numbered mode, a follow-up bullet that starts with four digits (for example "0042 fix the parser") has the digits dropped from its base slug, giving `0005-fix-the-parser`. In plain mode the slug stays `0042-fix-the-parser`, as before.
- The selftest checks that a missing `<root>/config` means plain mode: the control case runs with no config file.

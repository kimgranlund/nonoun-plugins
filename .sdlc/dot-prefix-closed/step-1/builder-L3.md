<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `DOT_RE`. `load()` now keeps `.NNNN-<slug>` dirs. `problems()` adds the dot-folder status rule in every mode and runs the prefix/id rule on `slug.lstrip('.')`. `strip_prefix()` drops the dot, and the `cmd_check` warning counts dot folders as prefixed. `cmd_close` gets the `archive` rename, two new refusals, the `.<slug>` follow-up context, `; moved to .<slug>` in the output and the dry-run `rename` line. The module docstring and the `load`, `problems` and `cmd_close` docstrings are updated. The selftest `filer()` helper gains a `slug=` parameter, and a new `(u)` selftest block covers every listed case.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: printed `tickets selftest: PASS`, exit 0.
- Mutation run on a scratch copy of the plugin. I broke 12 things one at a time: load skipping dot dirs, no rename on the filer path, no rename on the reason path, no status rule, no lstrip in the prefix rule, no target refusal, no already-closed check, follow-up context naming the old folder, no dry-run line, archive always true, strip_prefix keeping the dot, and the warning ignoring dot folders. Each one made the selftest exit 1. Ten reported named misses; "no rename (reason)" and "archive always" crashed with a traceback instead.
- Handoff acceptance script, run from the repo root. Every line behaved as commented:
  - Close printed `...; moved to .0001-alpha`, exit 0.
  - The rename test exit 0.
  - `check` passed with `ok: 2 tickets`.
  - `grep -c` printed 1.
  - `new feature gamma` created `0003-gamma`.
  - The second close exited 1 with `0001-alpha: already closed (folder .0001-alpha); nothing written`.
  - `check` with `.hidden` and `.board-state.json` present passed with `ok: 3 tickets, roadmap current`.
  - After the status sed, `check` exited 1 with `.0001-alpha: closed ticket folder (dot prefix) has status 'ready'; want done or dropped ...`.
- Plain-mode negative control: exit 0, `$T2/delta` still exists and `$T2/.delta` does not.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (all selftests, shellcheck and plugin validate ok).
- `python3 plugins/sdlc-lite/scripts/tickets.py check` on this repo's `.sdlc`: `ok: 53 tickets, roadmap current`.

## Notes
- The handoff doesn't say whether the "rename target `.<slug>` already exists" refusal applies outside archive mode. I only apply it when `archive` is true, because a plain slug never moves, so an unrelated `.<slug>` dir can't block its close. The "already closed (folder .<slug>)" refusal applies in every mode, and it only fires when `<slug>/handoff.md` is missing anyway.
- On a close that renames, the `; moved to .<slug>` suffix comes last in the output, after any duplicate or `--skip` notes.
- `.sdlc/dot-prefix-closed/handoff.md` was already modified before this step started. I did not touch it.

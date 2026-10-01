<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `TICKET_ROOT_RE`, `ticket_dir(root)` and `strays(root)`.
  - All six commands (new, close, roadmap, check, archive, number) now resolve `td = ticket_dir(root)` first. They read and write ticket folders under `td`, and they add `strays(root)` to the problems that make them refuse.
  - `stamp()` takes its template from `<root>` and runs its exists check under `ticket_dir(root)`.
  - In `render()`, roadmap row links get a `tickets/` prefix only when the ticket root is `tickets`.
  - `outside_refs()` gains `roadmap=None`. close, archive and number pass `td` and `roadmap=root / 'roadmap.md'`.
  - Updated the docstring (first line, `--root`, config section with `ticket_root: tickets` and "outside the ticket root") and the `--root` argparse help.
  - Appended selftest cases, including a negative control for a root with no `ticket_root` line. No existing case changed.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- Acceptance criteria 1 to 9 (new under tickets/, numbered close with `--rewrite-refs` in git, cite refusal naming spec.md and not roadmap.md, number then archive, unsupported value, stray, docstring, the two mutation checks on `ticket_dir` and `strays`): all PASS. I ran them verbatim through a bash `eval` wrapper.
- Guards: selftest PASS; default-layout new/check PASS; base-vs-new `render` byte-identical on this repo's `.sdlc` PASS (with `SDLC_BASE_SHA=c6d39d0`, read from the step's base-sha file); changed-files scope PASS (only tickets.py outside `.sdlc`).
- Extra negative control: dropping the `roadmap=` keyword from `cmd_close` makes the new git selftest case fail, because `.sdlc/roadmap.md` gets listed as a cite. So that case discriminates.
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: PASS. `fanout.py selftest`: PASS. `traces.py selftest`: PASS. These modules import tickets.py.
- `git diff --check`: clean.

## Notes
- As the handoff scopes it, `id_floor`, the no-filer hint and the `close --dry-run` worktree lines still read other trees' `<root>`, not their `tickets/`. Step 2 covers that.
- `render()` now calls `ticket_dir(root)`, so an external caller rendering a root whose config has an unsupported `ticket_root` value gets `Fail`. All in-repo callers go through commands that resolve `td` first.
- The working tree also has modified or untracked files under `.sdlc/0177-*` and `.sdlc/0179-*`. They come from other runs; this step did not touch them.

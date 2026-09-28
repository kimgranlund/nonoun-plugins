<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - New module-level `rewrite_files(top, files, old, new)`. `cmd_close`'s `rewrite_now` now calls it; its output and ordering are the same as before.
  - `cmd_archive` has the new signature `(root, numbered=False, dry_run=False, rewrite_refs=False, force=False)`. It runs `outside_refs` for each target and refuses with hits (the dry run too). The dry run with `--rewrite-refs` prints sorted `rewrite <file>` lines.
  - On a real `--rewrite-refs` run, every citing file is rewritten before any rename, and the output ends with `; rewrote refs in ...`. `--force` leaves the files alone.
  - Argparse gains `--rewrite-refs` and `--force`, and `main` passes both through. The usage line and the `archive` docstring paragraph are updated.
  - Nine new selftest `expect`s go next to the archive block:
    - A committed cite refuses, names the file, and writes nothing. So does a dry run with no flag.
    - `--rewrite-refs` rewrites the file and renames the folders.
    - `--force` renames and leaves the cite.
    - A dry run with `--rewrite-refs` lists the file and writes nothing. A dry run with `--force` lists only the renames.
    - A cite between two archived folders refuses, and then `--rewrite-refs` rewrites it.
    - Outside git, archive does not scan.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- Negative control: in place, with a backup, I changed the scan's `if files]` to `if files and False]` and ran the selftest. It reported "FAIL, these did not bite" and listed 6 `archive refs` expects. I restored the file and the selftest passed again.
- Acceptance criteria 2 to 9: I ran each command as written, with `$T` standing for the script path. All exited 0: refuse and folder kept; refusal names `spec.md`; `--rewrite-refs` rewrites and renames; `--force` renames and leaves the cite; dry run with `--rewrite-refs` prints `rewrite spec.md` and writes nothing; dry run with no flag names `spec.md`; cite between two folders is rewritten and both are renamed; outside git (guard) still renames.
- Criteria 10 to 12 (the three `grep -q` checks for the usage line and the `rewrite_refs=True` and `force=True` selftest calls): each exited 0.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0, run after the final edit.
- `git diff HEAD -- plugins/sdlc-lite/scripts/tickets.py | grep '^-'` shows 11 lines:
  - the file header,
  - the old usage line and the two old lines of the `archive` docstring paragraph,
  - the 3 lines of the moved `rewrite_now` loop,
  - the old `cmd_archive` def plus its 2 replaced return lines,
  - the old `--dry-run` argparse help line.
  No `close` selftest expect line was removed.

## Notes
- Removed lines also include the usage line, the archive docstring paragraph, and the archive `--dry-run` help line. Step items 7 and 8 require these changes, but criterion 13 lists only `rewrite_now`, `cmd_archive` and `main` as allowed removals.
- The refusal message reads:
  - `archive would rename these folders, but other files reference them:`
  - one `<old>:` line per cited folder, with its citing files indented two spaces below it
  - `rerun with --rewrite-refs (rewrite them to the dot form) or --force (archive anyway, leaving them); nothing written`
- The `outside_refs` docstring still says "for a numbered close". I kept it unchanged so the diff stays inside criterion 13's list of allowed removals.
- Step 2 covers the other docs: the ticket skill, the repo CLAUDE.md, and `sdlc-lite-author.md`.

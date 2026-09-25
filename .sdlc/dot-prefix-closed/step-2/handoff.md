## Task goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/` so Finder and `ls` hide finished work, and every tool still treats it as a closed ticket.

## Step 2: `tickets.py archive` renames existing closed numbered folders
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, add `cmd_archive(root, numbered=False, dry_run=False)`, a `run()` dispatch for `archive`, and an argparse subparser `archive [--dry-run] [--numbered]`. Add `archive` to the `kw` command tuple in `main`, plus the Usage/docstring line.

Behavior:
- Outside numbered mode (no flag, no config line), refuse: `archive renames NNNN-<slug> folders and needs numbered mode (--numbered or ticket_folders: numbered in <root>/config); nothing written`.
- Refuse on `problems(ts, numbered)`, writing nothing.
- Candidates: folders that match `PREFIX_RE`, are not dot folders, and have `status` in (`done`, `dropped`). Plain-slug folders are never touched.
- If any target `.<name>` exists, refuse before any rename and write nothing.
- `--dry-run` prints one `<name> -> .<name>` line per candidate and writes nothing.
- Otherwise rename every candidate, regenerate the roadmap, and persist the config when `--numbered` was passed. Output is `archived N folder(s): ...`, or `nothing to archive` when there are no candidates.
- Selftest `expect`s cover:
  - done and dropped both move, and a ready ticket stays
  - dry run writes nothing (`snap` equal)
  - a collision refuses with `snap` equal
  - plain mode refuses with `snap` equal
  - a second run reports nothing to archive
  - `check` passes after archive
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints PASS.
- In a temp numbered root with `0001-a` (done), `0002-b` (dropped) and `0003-c` (ready), all ids valid and the roadmap current:
  - `archive --dry-run` exits 0, prints `0001-a -> .0001-a` and `0002-b -> .0002-b`, and leaves the tree unchanged (`ls -A` is the same before and after).
  - `archive` exits 0 and leaves `.0001-a`, `.0002-b` and `0003-c`.
  - `check` then exits 0.
  - A second `archive` prints `nothing to archive`.
- In a plain root (no config, no flag), `archive` exits 1 and names numbered mode.
- `python3 plugins/sdlc-lite/scripts/tickets.py archive --help` lists `--dry-run` and `--numbered`.

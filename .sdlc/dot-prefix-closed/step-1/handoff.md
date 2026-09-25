## Task goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/` so Finder and `ls` hide finished work, and every tool still treats it as a closed ticket.

## Step 1: tickets.py recognizes `.NNNN-<slug>` folders, checks their status, and close renames into them
level: L3
### Do
Only `plugins/sdlc-lite/scripts/tickets.py` changes.
- Add `DOT_RE = re.compile(r'\.\d{4}-[a-z0-9]+(-[a-z0-9]+)*')`, matched with fullmatch. This is a closed-ticket folder: a dot, 4 digits, a dash, then a slug.
- `load()`: keep a dir when it does not start with `_` or `.`, or when `DOT_RE.fullmatch(name)`. This is mode-independent, so the id allocation in `stamp()`, `depends`/`from` resolution in `problems()`, `order()` and `render()` all see dot folders with no further change. `_templates`, `.board-state.json` (a file), and any other dot dir such as `.hidden` stay skipped.
- `problems(ts, numbered)`:
  - (a) In any mode, a slug matching `DOT_RE` whose `status` is not `done` or `dropped` adds this error: `{slug}: closed ticket folder (dot prefix) has status {s!r}; want done or dropped (rename it to {slug[1:]} to reopen)`.
  - (b) In numbered mode, run the existing prefix/id rule on `slug.lstrip('.')` for dot folders, so `.0005-alpha` with id T-0001 still fails.
- `strip_prefix()`: drop one leading `.` when `DOT_RE` matches, before stripping `NNNN-`. The follow-up duplicate check then covers closed tickets.
- `cmd_check` warning ("every ticket folder has an NNNN- prefix"): count a `DOT_RE` folder as prefixed.
- `cmd_close`: work out `archive = numbered and PREFIX_RE.match(slug)`. Plain slug folders never move, even in numbered mode.
  - Before anything is written, on both the filer path and the `--reason` path, refuse when `root / ('.' + slug)` already exists. The message names it and says nothing was written.
  - When `root / slug` has no handoff but `root / ('.' + slug)` has one, refuse with `already closed (folder .<slug>)`.
  - When `archive` is true: after the handoff (and any follow-ups) is written, rename `root/slug` to `root/('.'+slug)`, then regenerate the roadmap from `load(root)`, then persist the config as today.
  - Each follow-up's `## Context` line names the final folder (`.<slug>/filer-L1.md`).
  - The success output adds `; moved to .<slug>`.
  - `--dry-run` adds the line `rename <slug> -> .<slug>` and writes nothing.
- Update the module docstring: the close text, and the "Dirs starting with _ or . are skipped" line, which gains the `.NNNN-<slug>` exception.
- Selftest additions, each an `expect`:
  - numbered close with a filer renames `0003-x` to `.0003-x`
  - numbered `--reason` close renames
  - the rename target already exists: refuse, and `snap` is unchanged
  - closing again by the old name refuses with "already closed"
  - `roadmap` lists `.0003-x`
  - a ticket with `depends: [T-0003]` passes `check`
  - the next `new --numbered` gets T-0004 or higher
  - `check` fails on a dot folder with `status: ready` (message contains `done or dropped`)
  - a `dropped` dot folder passes
  - `.hidden/handoff.md` with front matter and a `.board-state.json` file do not change the ticket count
  - negative control: a plain-mode close does not rename
  - negative control: numbered mode with a plain-slug folder (`alpha`) does not rename, and the existing cases (i), (j), (o) stay green
  - the dry run shows the rename line and writes nothing
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS`, exit 0.
- Run this script from the repo root. Every command in it behaves as commented:
  ```
  P=plugins/sdlc-lite/scripts/tickets.py; T=$(mktemp -d)/.sdlc
  python3 $P --root $T new feature alpha --numbered && python3 $P --root $T new feature beta --numbered
  sed -i '' 's/^depends:.*/depends: [T-0001]/' $T/0002-beta/handoff.md && python3 $P --root $T roadmap
  python3 $P --root $T close 0001-alpha --reason "test"        # exit 0, output contains "moved to .0001-alpha"
  test -d $T/.0001-alpha && test ! -e $T/0001-alpha            # renamed
  python3 $P --root $T check                                    # exit 0: depends on T-0001 resolves
  grep -c '\.0001-alpha' $T/roadmap.md                          # >= 1
  python3 $P --root $T new feature gamma                        # creates 0003-gamma (config decides numbered), not 0001-*
  python3 $P --root $T close 0001-alpha --reason again          # exit 1, stderr contains "already closed"
  mkdir $T/.hidden && printf -- '---\nid: T-0009\n---\n' > $T/.hidden/handoff.md && touch $T/.board-state.json
  python3 $P --root $T check                                    # exit 0, "ok: 3 tickets"
  sed -i '' 's/^status:.*/status: ready/' $T/.0001-alpha/handoff.md
  python3 $P --root $T check                                    # exit 1, stderr names .0001-alpha and "done or dropped"
  ```
- Plain-mode negative control: `T2=$(mktemp -d)/.sdlc; python3 $P --root $T2 new feature delta && python3 $P --root $T2 close delta --reason x` exits 0, `$T2/delta` still exists, and no `$T2/.delta` exists.

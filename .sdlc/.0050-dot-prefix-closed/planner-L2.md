<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
In numbered mode, closing a ticket renames `.sdlc/NNNN-slug/` to `.sdlc/.NNNN-slug/`. tickets.py (new, close, roadmap, check, depends), board.py and steps.py keep treating that dot folder as a closed ticket. A one-shot `tickets.py archive` renames existing closed folders. Plain mode does not change.

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

## Step 3: board.py and steps.py handle dot ticket folders, with selftests to prove it
level: L2
### Do
`plugins/sdlc-lite/scripts/board.py` already lists every dir with a `handoff.md` (`root.iterdir()` at the `summary()` and `main()` candidate lists) and has no dot filter. `plugins/sdlc-lite/scripts/steps.py` takes an explicit path. So no code change is expected in either script. Change code only if a new selftest fails, and keep any change minimal.
- Add board.py selftest cases in a temp root:
  - `.0003-closed-work`, done, with a `planner-L1.md`, renders with ID `T-0003`
  - `.0004-closed-bare`, done, with no step work, is hidden
  - `.0005-gone`, dropped, is hidden
  - a `_templates/feature.md` dir and a `.board-state.json` file produce no row
  - `--task .0003-closed-work` renders that one task
  - under the default id sort, the dot folder sorts by its id among the other tickets
- Add a steps.py selftest case: `split` on a task dir named `.0003-x` (holding a planner file and a handoff with front matter) writes `.0003-x/step-1/handoff.md`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
- Run this in a temp root:
  - Tickets: `.0001-a` (done, with `planner-L1.md`), `.0002-b` (done, no step work) and `0003-c` (ready).
  - Non-tickets: a `_templates/feature.md` and a `.board-state.json`.

  `python3 plugins/sdlc-lite/scripts/board.py --root <root>` output contains `.0001-a` and `0003-c`, and does not contain `.0002-b`, `_templates` or `board-state`.
- `git diff --stat plugins/sdlc-lite/scripts/board.py plugins/sdlc-lite/scripts/steps.py` shows selftest-only changes, or a stated minimal fix.

## Step 4: Docs describe dot-prefix closed folders and `archive`
level: L1
### Do
Update the records that describe tickets.py behavior:
- `/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets9/CLAUDE.md`, the Layout `scripts/tickets.py` line:
  - in numbered mode, `close` renames `NNNN-<slug>` to `.NNNN-<slug>`
  - every tool treats a `.NNNN-<slug>` folder as a closed ticket
  - `check` fails on a dot folder that is not done or dropped
  - `archive [--dry-run]` renames existing done/dropped numbered folders
  - `_templates` and other dot entries stay skipped
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add `archive [--dry-run] [--numbered]` to `argument-hint`, and extend the numbered-folders rule to match.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the layout block (lines about 9 to 24), add a `.sdlc/.NNNN-<slug>/` closed-ticket entry. In the Ticket front matter paragraph, add the close rename.
- `plugins/sdlc-lite/skills/file/SKILL.md`, step 4: add one clause saying that in numbered mode the folder becomes `.NNNN-<slug>` after close.
- `.claude/agents/sdlc-lite-author.md`, Invariants: add the dot-prefix close/archive rule to the numbered-mode sync line.

Use no em dashes.
### Acceptance criteria
- `grep -n '\.NNNN-' CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md plugins/sdlc-lite/skills/handoff-format/SKILL.md .claude/agents/sdlc-lite-author.md` finds at least one hit in each file.
- `grep -n 'archive' CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md` finds a hit in each.
- `grep -rn '—' CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/skills/file/SKILL.md .claude/agents/sdlc-lite-author.md` prints nothing.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The CLAUDE.md validate warning is expected.

## Risks
- Recognizing `.NNNN-<slug>` in `load()` does not depend on the mode. A plain-mode repo that already has a `.NNNN-<slug>/handoff.md` with front matter would start being read as a ticket. That is unlikely, but it bends "plain mode unchanged". Gating it on numbered mode would need board.py to read the config, and it could let `new` reuse ids.
- `close` takes the folder name (`0003-gamma`). A caller that passes the bare slug in numbered mode already fails today, and this plan does not fix that.
- `/file` and `/chain` may keep `.sdlc/<slug>/` paths in memory after close. Once the folder moves they would be stale. After close, only the board reads it again.
- The `archive` rule "dropped moves too" and "config decides numbered for /file" follow the handoff's default gaps, not an explicit user answer.
- Step 3 assumes board.py and steps.py need no code change. If `sort_tasks` or `summary` handles a leading dot badly, the builder will need a small code fix.

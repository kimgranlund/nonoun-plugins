<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0050: Dot-prefix closed ticket folders

## PR body
### Summary
In numbered mode, `tickets.py close` now renames `.sdlc/NNNN-<slug>/` to `.sdlc/.NNNN-<slug>/`, so Finder and `ls` hide finished work. Every tool still reads the dot folder as a closed ticket, including `new` id allocation, `roadmap`, `check`, `depends` resolution, `board.py` and `steps.py`. A new one-shot `tickets.py archive` renames closed folders that already exist. Plain mode is unchanged.

### Changes
1. **`scripts/tickets.py`: recognize dot folders, rename on close**
   - Adds `DOT_RE`, which matches a dot, 4 digits, a dash and a slug. `load()` keeps folders that match it. `_templates`, `.board-state.json` and other dot entries are still skipped.
   - `check` fails on a dot folder whose status is not `done` or `dropped`. In numbered mode the prefix/id rule also applies to dot folders.
   - `strip_prefix()` removes the dot, so the follow-up duplicate check also covers closed tickets. The all-prefixed warning counts dot folders as prefixed.
   - `close` renames `NNNN-<slug>` folders after writing, on both the filer path and the `--reason` path. A plain-slug folder is never renamed, even in numbered mode.
     - It refuses when the rename target already exists.
     - It refuses with `already closed (folder .<slug>)` when the ticket was already closed and renamed.
     - Output ends with `; moved to .<slug>`, and `--dry-run` prints the `rename` line.
2. **`tickets.py archive [--dry-run] [--numbered]`**
   - Renames existing `done`/`dropped` numbered folders and regenerates the roadmap.
   - Refuses, writing nothing, in each of these cases: outside numbered mode, on any `check` problem, or when a target already exists.
3. **`scripts/board.py`, `scripts/steps.py`**: new selftest cases only. Neither script's logic needed a change.
4. **Docs** now describe the rename, the dot-folder rule and `archive`:
   - `CLAUDE.md` (the tickets.py line under Layout)
   - `skills/ticket/SKILL.md`
   - `skills/handoff-format/SKILL.md`
   - `skills/file/SKILL.md`
   - `.claude/agents/sdlc-lite-author.md`

### Verification
- **Step 1: pass (verifier L2).**
  - `tickets.py selftest` passes.
  - The verifier broke the code five ways, one at a time. Each change turned the selftest red (the builder separately ran 12 such changes).
  - The acceptance script behaved as commented in every line: rename, `check` resolving a `depends` on the closed ticket, the roadmap listing `.0001-alpha`, `new` not reusing the id, the "already closed" refusal, `.hidden`/`.board-state.json` ignored, and `check` failing on a dot folder with `status: ready`.
  - The same script run at HEAD fails, so the checks tell old behavior from new.
  - Plain-mode negative control: the folder is not renamed.
- **Step 2: pass (verifier L1).**
  - Selftest passes, and making the rename a no-op turned it red.
  - Checked by hand: `--dry-run` leaves `ls -A` unchanged; archive leaves `.0001-a`, `.0002-b` and `0003-c`; `check` passes afterward; a second run prints `nothing to archive`; a plain root refuses; `--help` lists both flags.
  - The collision and plain-mode selftest cases were checked by reading the diff, not by breaking the code.
- **Step 3: pass on the second verification (verifier L1).**
  - The first verification failed only on criterion wording. The legacy `.board-state.json` hint line, which CLAUDE.md documents, contains `board-state`, which the criterion literally banned; no code defect was found.
  - Both selftests pass. Adding a dot-name filter to board.py's task list turned the board selftest red.
  - On a hand-built root, only the expected table rows render.
- **Step 4: pass (verifier L1).**
  - Grep checks find the new text in each doc and no em dashes. The same greps at HEAD find nothing, so they bite.
  - `scripts/check.sh` exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added: in numbered mode, `tickets.py close` renames a ticket folder to `.NNNN-<slug>` so closed work is hidden from Finder and `ls`. Every tool (tickets.py, board.py, steps.py) still treats it as a closed ticket, and `check` fails on a dot folder that is not done or dropped. New `tickets.py archive [--dry-run] [--numbered]` renames existing done/dropped numbered folders.

## Follow-ups
- tickets.py `load()` reads `.NNNN-<slug>` folders as tickets in plain mode too, so a plain-mode repo that already has such a folder with front matter would start seeing it as a ticket; decide whether to gate this on numbered mode.
- In numbered mode, `tickets.py close <bare-slug>` fails because it needs the `NNNN-<slug>` folder name; resolve a bare slug to its numbered folder so `/file` and `/chain` callers cannot trip on it.

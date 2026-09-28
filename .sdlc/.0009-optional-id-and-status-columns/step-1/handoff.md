## Task goal
`/board` shows each task's ticket id and ticket status without changing the board for task dirs that have no ticket front matter. (Ticket T-0009, `.sdlc/0009-optional-id-and-status-columns/handoff.md`; read its Intent and Constraints.)

Repo root: the git work tree containing this `.sdlc/`. All commands run from there.

## Step 1: Add ID/Ticket columns to board.py, reusing tickets.py's parser, with a regression check that bites
level: L3
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Import `tickets` (same `scripts/` dir, so no path changes needed) and use `tickets.parse(text)` to read `id` and `status` from each task's `handoff.md`. Wrap the read/parse in `try/except` so any exception `tickets.parse`/file IO can raise is treated as "no front matter" (empty `id`/`status`), per the handoff's explicit requirement that a bad file must not crash the board.
- In `main()`, after building `tasks` (and after the `--task` filter is applied, since only rendered tasks decide whether the columns appear), parse each task's front matter once. If any parsed task has a non-`None` result, switch the header/separator from `| Task | Step | Status | % |` to `| ID | Task | Ticket | Step | Status | % |` (columns in that order, per the handoff's delta) and add `| id | task | step |cell | pct |`-shaped rows with `id`/`status` (or empty string) inserted at the right positions; otherwise keep today's byte-identical 4-column table.
- Update the module docstring (lines 1-18) to mention the new columns and their opt-in condition.
- Do not touch `summary()` (the `--summary` line format) or `.board-state.json` key format (`f'{task}/{step}'` stays as is) — these are explicit non-goals.
- Add a `board.py selftest` subcommand (mirroring the pattern already in `tickets.py`'s `selftest()`/`run()`/`main()`) that builds temp fixtures in a `tempfile.TemporaryDirectory()` and asserts, as negative and positive controls:
  - a task dir with a valid ticket-front-matter `handoff.md` produces a row containing that ticket's `id` and `status`, and the header includes `ID` and `Ticket`;
  - a task dir with no front matter (or a `handoff.md` that makes `tickets.parse` raise) mixed into the same render still produces the 6-column table with empty `ID`/`Ticket` cells for that task, and does not crash;
  - a render where *no* task has front matter produces the exact 4-column table (byte-for-byte matches the pre-change format), confirming the opt-in gate works;
  - `--summary` output is unaffected by the presence of front matter (still uses the old format).
  Wire `plugins/sdlc-lite/scripts/check.sh` to run `python3 "$root/scripts/board.py" selftest` alongside the existing `tickets.py selftest` line, `|| fail=1`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints a PASS line and exits 0; temporarily breaking the column-gate logic (e.g. commenting out the "any front matter" check) makes it fail, proving the check bites.
- `python3 plugins/sdlc-lite/scripts/board.py` run from the repo root (where `.sdlc/` lives) shows `ID` and `Ticket` columns with a row containing `T-0009` and `proposed` or `ready` (this task's own ticket).
- `python3 plugins/sdlc-lite/scripts/board.py --root plugins/sdlc-lite/bench/results` output is byte-identical to `.sdlc/0009-optional-id-and-status-columns/baseline-bench-board.txt`.
- `python3 plugins/sdlc-lite/scripts/board.py --summary` output matches the format captured in `.sdlc/0009-optional-id-and-status-columns/baseline-summary.txt` (same task/pct/counts shape; content may legitimately differ if task state moved on since the baseline was captured).
- `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Task goal
/board can list tasks in the same order as the roadmap (by ticket id, or by folder name) instead of by recency. Default order stays `recent`.

## Step 1: Add `--sort` to board.py, cover it in selftest, document it
level: L2
### Do
- In `plugins/sdlc-lite/scripts/board.py`:
  - Add `ap.add_argument('--sort', choices=['recent', 'id', 'name'], default='recent')` in `main()` (near the existing `--summary` argument, around line 373).
  - Add a `sort_tasks(tasks, mode)` helper (near `ticket_of`/`belongs_on_board`, e.g. after line 200):
    - `mode == 'name'`: `sorted(tasks, key=lambda t: t.name)`.
    - `mode == 'id'`: sort by `(0, int(numeric part of the ticket id), t.name)` for tasks whose `ticket_of(t)` returns an id (parse the numeric part of `T-NNNN` with a regex, matching the "numeric part of `T-NNNN`" wording in the handoff), and `(1, t.name)` for tasks with no ticket id (so they sort after all ticketed ones, alphabetically by folder name).
    - `mode == 'recent'` (default): the existing `key=lambda d: d.stat().st_mtime` behavior — must produce byte-identical output to the current unflagged behavior.
  - In `main()`, replace the current `tasks = sorted((d for d in root.iterdir() ...), key=lambda d: d.stat().st_mtime)` (line 384) with building the unsorted candidate list, calling `sort_tasks(candidates, a.sort)`, then applying the existing `belongs_on_board` filter (line 386) on the sorted list, so filtering never changes order.
  - Leave `--summary` and the ticket-hiding filter behavior untouched.
- In `plugins/sdlc-lite/skills/board/SKILL.md`:
  - Add `[--sort {recent,id,name}]` to the `argument-hint` frontmatter line.
  - In step 2, add passing `--sort <mode>` through to `board.py` when given, alongside `--task` and `--root`.
- Add selftest cases to `selftest()` in `board.py` (after the existing numbered cases, before the final `if misses:` block):
  - Create task dirs with ticket ids `T-0002` and `T-0003` where `T-0003`'s dir is created (and thus has the newer mtime) before `T-0002`'s; render/list with `--sort id` (via the `main()` subprocess pattern already used at line 346, or a direct call to the new sort helper) and assert `T-0002` precedes `T-0003` in the output regardless of mtime.
  - Add a mix of ticketed and non-ticketed task dirs and assert non-ticketed ones sort after ticketed ones, ordered alphabetically by folder name.
  - Create folders with names deliberately out of creation-order (e.g. `bravo` before `alpha`) and assert `--sort name` output lists them alphabetically.
  - Assert that omitting `--sort` (or passing `--sort recent`) produces output identical to today's mtime-based order (a regression check against the pre-change behavior).

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0 and prints `board selftest: PASS`, including the new sort cases.
- Manually: create `.sdlc/` fixtures where a `T-0003` task dir is newer (by mtime) than a `T-0002` task dir; `python3 plugins/sdlc-lite/scripts/board.py --sort id` lists the `T-0002` row before the `T-0003` row.
- `python3 plugins/sdlc-lite/scripts/board.py --sort name` on a set of folders lists them in strict alphabetical order by folder name.
- `python3 plugins/sdlc-lite/scripts/board.py` with no `--sort` flag produces output identical to the pre-change behavior (same as `--sort recent`) on the same fixtures.
- `plugins/sdlc-lite/skills/board/SKILL.md` has `--sort {recent,id,name}` in `argument-hint` and step 2 mentions passing `--sort` through.
- `scripts/check.sh` passes.


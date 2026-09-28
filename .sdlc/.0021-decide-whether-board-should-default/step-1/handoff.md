## Task goal
With no `--sort` flag, `board.py` orders by ticket id when any rendered task has ticket front matter, with unticketed tasks after it in mtime order. Otherwise it keeps recency order, and an explicit `--sort` behaves exactly as before.

## Step 1: Add the default sort branch in board.py and prove it in the selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Change `--sort` to `default=None` (keep `choices`). In `main()`, filter with `belongs_on_board` first, then sort, so the default is decided over the rendered tasks only.
- In `main()`, when `a.sort` is None:
  - Use `mode='id'` with mtime tie-breaking for unticketed tasks if `any(ticket_of(t) for t in tasks)`.
  - Otherwise use `'recent'`.
- Add this to `sort_tasks`: a mode, for example `'auto'`, that sorts ticketed tasks by numeric id first. Unticketed tasks follow, ordered by mtime and not by name.
  - Explicit `'id'` must keep its current unticketed-by-name order. Update the `sort_tasks` docstring.
- Leave `--summary` and `--task` paths untouched. `--task` still works because it filters the already-sorted list.
- Update selftest section 6:
  - Existing `srt` fixture, which has tickets: no flag gives `['yankee-two','zulu-three','bravo','alpha']`. The unticketed tasks are in mtime order (bravo mtime is lower than alpha's in the fixture, so alpha is the later one). Recompute the expected order from the utime values; do not hard-code it blindly.
  - Explicit `--sort id` still gives `alpha, bravo` (by name) after the ticketed tasks.
  - `--sort recent` and `--sort name` are unchanged.
  - Add a second fixture with no ticketed tasks. It proves no flag equals `--sort recent` and gives mtime order.
  - Replace the old "no --sort equals --sort recent" assertion so it uses the no-ticket fixture. Delete `.board-state.json` between runs, as the existing test does.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS`.
- In a temp root with two ticketed tasks (T-0003 older, T-0002 newer) and one unticketed task, `board.py --root <tmp>` lists T-0002 before T-0003 and the unticketed task last.
- In a temp root with no ticketed tasks, `board.py --root <tmp>` output equals `--sort recent` output.
- `--sort id`, `--sort name` and `--sort recent` order the same fixture as before. The unticketed pair under `--sort id` is still by name.
- `board.py --summary` output is unchanged on a fixture root.
- `board.py --task <slug>` still renders only that task.

## Risks
- A `/chain` render without `--task` may now show tasks in a different order when tickets exist. This is intended, but verify no doc or script assumes newest-last.
- `statusline.sh` uses `--summary`, which is not affected, but confirm `summary()` does not call `sort_tasks` with the default.
- The selftest expected order depends on the fixture mtimes. The builder must derive it from the `os.utime` values.

<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/order.py selftest` exits 0: pass. Evidence: ran it; 15 `ok:` lines, `order selftest: PASS`, `exit=0`. The check bites: the mtime negative control below turned 5 of the 15 red.
- `grep -n "mtime\|stat()" plugins/sdlc-lite/scripts/order.py` prints nothing: pass. Evidence: `grep exit=1`, no output, on the existing file (`ls -l` shows `order.py`, 10188 bytes, executable). The module uses `os.utime` only inside `selftest()`, which matches neither pattern.
- Fixture copy with `touch -t 202601010000`, `newest <tmp> verifier` ends `verifier-L2.md`, `newest <tmp> builder` ends `builder-L3.md`: pass. Evidence: `cp -R .../step-2/. $tmp; touch -t 202601010000 $tmp/*` (ls shows every file `Jan 1 2026`); output `.../tmp.sc0lXkM5yM/verifier-L2.md` and `.../tmp.sc0lXkM5yM/builder-L3.md`. With equal mtimes, an mtime rule could not have produced this.
- Negative control, sort key changed to `st_mtime` in a scratch copy: pass. Evidence: scratch `order.py` line 93 became `names.sort(key=lambda n: os.stat(...).st_mtime)`; selftest printed `order selftest: FAIL, these did not hold:` (a) ×2, (b) highest k, (c) ordering, (e) newest; `NC exit=1`. Biting variable: cases (a), (b)-pairing, (c), (e) set mtimes inverse to the true order.
- `run-selftest.sh` prints `run selftest: PASS`; `jq -r .file` gives the three names in order; removing `file` from run.sh makes it FAIL: pass. Evidence: `bash plugins/sdlc-lite/scripts/run-selftest.sh` → `run selftest: PASS`, `exit=0`. A scratch copy of the selftest that keeps its temp dir (same run.sh) → `jq -r .file` printed `planner-L3.md`, `planner-L3-2.md`, `planner-L3-3.md`; the raw lines carry `"file":"planner-L3.md"` etc. Negative control: throwaway worktree at HEAD (`grep -c 'file: $file'` on HEAD's run.sh = 0), new run-selftest.sh copied in and run against HEAD's run.sh → `run selftest: FAIL: runs.jsonl file fields are 'MISSING MISSING MISSING '`, `NC exit=1`. Worktree removed; `git worktree list` shows only the two original checkouts.
- Extra: `bash plugins/sdlc-lite/scripts/check.sh` → `check exit=0` and its output includes `order selftest: PASS` (check.sh:13 calls `order.py selftest`). run.sh:61 still uses `ls -t` for the verifier swap, left for Step 4 as the handoff asked.

## Out of scope changes
`.sdlc/0049-newest-by-mtime/handoff.md` gained a "Conductor notes" section (modified 19:17, before the builder ran at 19:20; not the builder's edit, and not part of this step). Untracked `.sdlc/0049-newest-by-mtime/planner-L2.md`, `runs.jsonl`, `step-2..5/` are chain artifacts. No other unexpected changes; `git status` shows only the four scripted files plus the new `order.py`.

## For the next attempt
None. Note for Step 4: builder correctly flagged that `board.py`'s docstring, `steps.py` split help, and run.sh's "readers take the newest file" still say mtime; they are due in the doc-update step.

## Task goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Step 3: steps.py and tickets.py pick the newest planner and filer through order.py
level: L2
### Do
- `plugins/sdlc-lite/scripts/steps.py`:
  - `find_plan` uses `order.newest(target, 'planner')`, keeping the "no planner-*.md" Fail message.
  - Update the docstring and the argparse help ("by mtime").
  - Rewrite selftest case (c). Two planner files with equal mtimes plus a runs.jsonl that records the lower-named file last: that file is used. Add a variant with inverse mtimes that gives the same result. Also cover no runs.jsonl: level then k order, so `planner-L3.md` beats `planner-L2.md`.
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `filers = order.ordered(d, 'filer')` (line 465).
  - Rewrite selftest (h) the same way: equal mtimes, with runs.jsonl deciding the order. Include an inverse-mtime variant, and a fallback to name order when there are no records.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` and `python3 plugins/sdlc-lite/scripts/tickets.py selftest` both exit 0.
- `grep -n "st_mtime" plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/scripts/tickets.py` shows only steps.py's snapshot helper (about line 191, which checks that nothing was written) and no ordering use.
- Negative control: restoring the mtime key in `find_plan` or in tickets.py line 465 makes the rewritten (c) or (h) case fail.

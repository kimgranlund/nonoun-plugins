<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: `find_plan` now uses `order.newest(target, 'planner')` and keeps the "no planner-*.md" Fail message. The docstring and argparse help no longer say "by mtime". Selftest (c) is rewritten into three cases: equal mtimes decided by runs.jsonl, inverse mtimes with the same result, and no runs.jsonl where `planner-L3.md` beats a newer `planner-L2.md`.
- `plugins/sdlc-lite/scripts/tickets.py`: filers now come from `run_order.ordered(d, 'filer')`, around line 467. Selftest (h) is rewritten into three cases: equal mtimes decided by runs.jsonl, inverse mtimes, and no records falling back to name order against a newer mtime.

## Checks
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS, exit 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, exit 0.
- `grep -n "st_mtime" steps.py tickets.py`: one hit, `steps.py:198`, in the snapshot helper. No ordering code reads mtime.
- Negative control: I put back the mtime-based `max` in `find_plan` and the mtime `sorted` in tickets.py. All three (c) cases and all three (h) cases then failed, and both selftests exited 1. I restored both files from backup, and both selftests pass again.

## Notes
- tickets.py already defines a function named `order` (line 156), so it imports the module as `import order as run_order`. steps.py uses a plain `import order`. Both rely on the scripts dir being on `sys.path`, which holds when they are run as scripts.
- I did not run `scripts/check.sh`; the acceptance criteria do not require it.

<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest passes, including a numbered close (flag and config) with several follow-up bullets, asserting each folder matches `^\d{4}-` and its digits equal the follow-up's own id: pass. Evidence:
  - `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS`.
  - Case (i) at tickets.py ~L742-757 checks `re.match(r'\d{4}-', s) and s[:4] == m['id'][2:]` and the exact names 0003, 0004 and 0005.
  - A real CLI run with `close alpha --numbered` gave `0002-do-thing-one` (id T-0002) and `0003-do-thing-two` (id T-0003).
  - The check can go red: I ran a throwaway copy of the script with numbered forced off in close's loop, and its selftest failed. It crashed with a traceback, so the mutation was crude, but the check still went red.
- Plain close without the flag or config still creates bare-slug folders (negative control), with existing cases (a)-(h) unbroken: pass. Evidence:
  - Case (i) negative control asserts `['0042-fix-the-parser', 'add-retry-to-fetch', 'add-retry-to-fetch-2']`, and the selftest passes with (a)-(h) untouched.
  - The real CLI `close alpha` with no flag gave `do-thing-one` and `do-thing-two`.
  - A missing `<root>/config` is covered: the CLI run had no config file, and the selftest control has none either.
- Clash handling is checked against the final numbered name and appends `-2`: pass. Evidence: the selftest asserts that a pre-existing `0003-add-retry-to-fetch` gives `0003-add-retry-to-fetch-2`.

## Out of scope changes
None. `tickets.py` also carries Step 1's uncommitted changes, and the task `handoff.md` diff is Step 1's. Both are expected.

## For the next attempt
None

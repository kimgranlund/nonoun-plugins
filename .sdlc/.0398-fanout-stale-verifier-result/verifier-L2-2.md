<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `fanout.py selftest` exits 0 and the grep span for three `case 15 verdict T-0398` cases exits 0: pass. Evidence: selftest=0, grep=0; the base blob gives grep=1; on a base archive with only the selftest hunk applied the selftest exits 1 with two misses, and the third case is a negative control that holds on both trees.
- `solo_verdict` and `branch_verdict` both read through `newest_verifier` (fanout.py:790, 805, 1636) and no file mtime is read: pass. Evidence: grep for mtime exits 1 on the diff and on the whole file; ordering comes from order.ordered.
- `check.py` and `tickets.py check` exit 0: pass. Evidence: check=0, tickets=0.

## Out of scope changes
None. Only plugins/sdlc-lite/scripts/fanout.py (38 insertions, 8 deletions) outside the ticket folder.

## For the next attempt
None

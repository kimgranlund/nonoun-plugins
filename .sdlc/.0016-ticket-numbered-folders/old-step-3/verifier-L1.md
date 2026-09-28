<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- Selftest passes and includes a new mutation case where a `NNNN-<slug>` folder has an `id` with different digits and `check` fails naming the mismatch: fail. Evidence: `tickets.py selftest` prints PASS, but only because the step-3 rule is absent. A grep of `plugins/sdlc-lite/scripts/tickets.py` finds no folder-prefix-to-id rule in `problems()` and no mismatch mutation case. Line 749 is a step-2 check, not this one. The builder's own report says it backed the change out.
- A matching `NNNN-<slug>`/`id` folder passes `check`, and a plain-slug folder is not subject to the rule: fail. Evidence: no such selftest case exists in the tree, and `builder-L2.md` reports status "blocked".

## Out of scope changes
None. `git diff --stat` shows only `tickets.py` (184 lines changed, matching the builder's expected step-1/2 count) and the task handoff, plus untracked `.sdlc` artifacts.

## For the next attempt
The step is not built. The builder found a real conflict, and it needs a decision before a retry: in plain mode, `new feature 0007-gamma` produces a folder whose digits differ from the assigned id, and `close` turns follow-ups like `0042 fix the parser` into `0042-fix-the-parser` with a mismatched id. An unconditional prefix rule then rejects both. The step-2 selftests `plain mode still takes a digit-led slug as-is` and `(i) plain close keeps bare slugs` fail with the rule added.

Pick one of the builder's options: (a) plain-mode `new` and `close` avoid or rewrite a `NNNN-` prefix that doesn't match the id, and the two step-2 tests change to match. Or (b) enforce the rule only in numbered mode. Then re-plan this step with that decision and its selftest cases.

Process note: the builder's `git checkout` wiped the step-1/2 work and it was restored from a saved diff. It is intact now: the selftest passes and the diff is 184 lines.

<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- planner.md has `guard timeout:` and `specgate.py check`: pass. Evidence: the grep command exited 0. The diff adds the rule 14 sub-bullet.
- handoff-format SKILL.md has `guard timeout:`: pass. Evidence: grep exited 0. The diff adds the line after the `steps.py split` paragraph.
- chain SKILL.md and conductor.md have `specgate.py check`: pass. Evidence: grep exited 0. The diff extends the `review L1` bullet in chain and the plan-review bullet in conductor.
- sdlc-internals.md has `scripts/specgate.py` and `guard timeout:`: pass. Evidence: grep exited 0.
- cost-control.md has "A1 (T-0210) is built": pass. Evidence: grep exited 0. The diff shows the line 3 replacement.
- sdlc-planner-l2.toml has `guard timeout:`: pass. Evidence: grep exited 0. `codex_roles.py generate --check` prints "Codex agent definitions verified".
- Negative-control command (phrases removed in a copy of the plugin): pass. Evidence: I ran it and it printed `NCPASS`. The copy's check.py output was `FAIL agents/planner.md: spec gate text missing "guard timeout:"`, `FAIL scripts/run.sh: spec gate text missing "specgate.py check"`, and `FAIL scripts/run.sh: specgate.py check does not come before exec run_lifecycle.py`. The check goes red when the phrases are removed. On the real tree, `check.py` exits 0 with `ok: 19 role levels, 9 agents checked`.
- (guard) scope check, only the allowed files changed: pass. Evidence: the command printed `SCOPEPASS`. The `git status` output (the status that ran before the criterion commands) shows no untracked files outside `.sdlc`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it in 4:58, under the 900 s timeout. The tail shows `specgate selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`, `ok: plugin validate`, and no FAIL lines. I did not capture its exit code. I confirmed `check.py` on its own exits 0.
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: it printed "PASS: catalog parity, identity, skill routes, hook isolation and context links".
- (guard) `codex_roles.py generate --check`: pass. Evidence: it printed "Codex agent definitions verified".
- (guard) `tickets.py --root .sdlc check`: pass. Evidence: it printed "ok: 214 tickets, roadmap current".
- Other Do items: pass. `git diff --check` is clean, and a grep for em dashes in the changed files found none. The `check.py` diff shows docstring item 16, the phrase checks, an order check, and an in-script negative control for each. The control for the phrase check fires in the removed-phrase run above. The swapped-lines control sits in the else branch of the order check. It only runs on a tree that passes the order check, which includes the real tree.

Steelman: I considered failing check.sh for lack of a captured exit code. The builder would reply that every line of output was ok, that `check.py` exits 0 on its own, and that nothing in the output is a FAIL. That holds, so I dropped it.

## Out of scope changes
None. The changed files are the allowed set plus the regenerated Codex TOML files: `sdlc-conductor-l1.toml`, `sdlc-planner-l1.toml`, `sdlc-planner-l2.toml` and `sdlc-planner-l3.toml`. The guard passed.

## For the next attempt
None

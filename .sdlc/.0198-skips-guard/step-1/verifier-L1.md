<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Check fails for a fix ticket missing planner and filer entries, and leaves old-b alone: pass. I ran the fixture and it printed `lean-a: skips.md records lane fix but has no ## Skipped entry for planner, filer`, exit 1, with old-b not named (C1=0). The assertion needs rc=1 and the exact message, so an unguarded `check` would go red.
- (guard) Same ticket with both entries passes `check`: pass. Output was `ok: 2 tickets, roadmap current`, exit 0. The previous criterion is the un-negated form of this fixture and it fails, so this one can go red.
- `step-2.superseded-1` ignored and the verifier gap named: pass. Output was `lean-a: skips.md records lane lean but has no ## Skipped entry for verifier step 1`, with no "step 2" in it (C3=0).
- `close --reason` on a fix ticket missing entries refuses and leaves status unchanged: pass. The output has the problem line plus `add one "- skip: ..." line per role under ## Skipped in <path>/skips.md; nothing written`, and status is still `proposed` (C4=0).
- Filer-path `close` on a lean ticket with no planner result refuses: pass. The output names `no ## Skipped entry for planner`, and status is still `proposed` (C5=0).
- (guard) `close --reason` with entries succeeds: pass. Output was `T-0001 done (closed by reason: x)`, and status is `done` (C6=0).
- `grep -qF "(skips)"` in `tickets.py`: pass (C7=0).
- (guard) `tickets.py selftest`: pass. It printed `tickets selftest: PASS`, and the run was green on the built tree. Nothing was red, so I did not run the pre-build HEAD gate.
- `## Skipped` in the handoff-format SKILL.md: pass (C9=0).
- `## Skipped` in `docs/maintenance/sdlc-internals.md`: pass (C10=0).
- Only the three allowed files changed: pass. The negated diff check against `$SDLC_BASE_SHA` is empty (C11=0). `git status` shows only those three files modified, plus `.sdlc` artifacts.
- Pre-feature exemption holds on the real repo: pass. `tickets.py --root .sdlc check` printed `ok: 214 tickets, roadmap current`.

## Out of scope changes
None. The three modified files are the ones the handoff names, and the rest is untracked `.sdlc` run artifacts.

## For the next attempt
None

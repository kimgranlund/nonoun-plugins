# Defect fixes for 0.20.9 (2026-10-05)

Field defects from 0.20.7 and 0.20.8 conductors, filed as T-0258 to T-0272 (commit c4909ee). Three were fixed solo-sized; the rest are filed, not fixed.

## Fixed

| Ticket | Fix commit | Regression test (observed red before, green after) |
|---|---|---|
| T-0258 fanout numbered close ignored `ticket_root` | 44ed997 | fanout selftest "untracked config lane": before, `merged, close refused: .sdlc/0001-x/handoff.md: missing or has no front matter, so it is not a ticket; nothing written`; after, `fanout selftest: PASS` |
| T-0261 `## Goal` precheck before planner or reviewer | c23fb94 | run-selftest.sh "goal precheck": before, `planner on a handoff with no ## Goal exited 0, want 2`; after, `run selftest: PASS`. steps.py selftest "(precheck)" cases pass. |
| T-0263 stale-lane block routed to replan | 8ed117d | steps.py selftest "next resplit": before, it failed; after, `steps selftest: PASS` |

Cause of T-0258: `.sdlc/config` is gitignored in the field repo, so the fresh integration worktree had no `ticket_root` line and `tickets.py close` looked in `<root>/<slug>`. fanout now copies the config into its worktrees when missing. T-0261 adds `steps.py precheck <task dir>`, which `run.sh` calls for a planner or plan-reviewer on a task handoff (exit 2, before any attempt record). T-0263 adds the `resplit` action for a blocked builder whose Notes start `stale lane:`; builder.md, the chain skill, and sdlc-internals.md name it, and the Codex builder agents were regenerated.

## Verification

One verifier handoff covered all three: `.sdlc/verify-defect-fixes-0209/` (verifier L3, model fable, builder was Sonnet). Verdict pass. It reverted each fix in a throwaway worktree and saw each test fail (fanout, run-selftest, steps), and ran fanout, steps, run-selftest, check.py, `codex_roles.py generate --check`, and check-packaging.py green. Its note: conductor.md:32 and level-rubric still say "builder blocked -> replan" unconditionally (they defer to `steps.py next`).

Tickets closed with `tickets.py close --reason`.

## Filed, not fixed

T-0259 (B), T-0260 (C), T-0262 (D close citations), T-0264 (F), T-0265 (G), T-0266 (H), T-0267 (I), T-0268 (J), T-0269 to T-0271 (K), T-0272 (L).
J: `docs/references/sdlc-internals.md` already documents `solo_run.py`; the ticket checks the conductor and solo agent text.

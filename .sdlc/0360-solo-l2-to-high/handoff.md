---
id: T-0360
title: "Drop solo L2 (sonnet) from xhigh to high; lock an eval"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Solo L2 runs on sonnet at effort high instead of xhigh, with an eval recorded and the model table lock updated.

## Intent
- Do: change the solo L2 row in plugins/sdlc-lite/adapters/claude/levels.json from ["sonnet", "xhigh"] to ["sonnet", "high"] (the user authorized exactly this change on 2026-10-07). Update everything that is checked against that row: run.sh, the level rubric (skills/level-rubric), the generated Claude agent definitions (claude_roles.py generate) and Codex files if affected (codex_roles.py generate), and any doc line that states solo L2 is xhigh (grep for it; dated reports stay history). Record the eval with `evals.py add` (role solo, level L2, model sonnet, effort high, host claude, task_set "T-0343 to T-0350 (8) and T-0271, T-0274, T-0304, T-0314, T-0323 (5), high vs xhigh", pass_rate 13/13 own checks, evidence docs/reports/2026-10-07-solo-l2-effort-sweep.md and docs/reports/2026-10-07-solo-l2-effort-sweep-2.md, result: high matched xhigh on every verdict at 29 to 39 percent of the cost; blind reviewer 4/5 on both arms, the one fail identical and a ticket-text artifact; limits one run per arm) and lock it with `evals.py lock`; read the existing .sdlc/evals/0002 and 0003 for the shape and evals.py --help for lock usage.
- Non-goals: any other model or effort row.
- Done when:
  - `grep '"solo"' plugins/sdlc-lite/adapters/claude/levels.json` shows L2 as ["sonnet", "high"]; check.py, claude_roles.py generate --check, codex_roles.py generate --check, run-selftest.sh, evals.py check, tickets.py check pass.
  - A negative control: with the eval lock removed or stale, evals.py check fails (observed).

## Context
Two sweeps: docs/reports/2026-10-07-solo-l2-effort-sweep.md (8 tickets, high $4.69 vs xhigh $15.32) and ...-sweep-2.md (5 L2 tickets, own checks 5/5 both arms, blind reviewer 4/5 both, high $6.15 vs xhigh $21.48 by session cost). Zero verdict disagreements. Reversible by this one row.

## Constraints
No em or en dashes. No push or publish. Do not change any row other than solo L2.

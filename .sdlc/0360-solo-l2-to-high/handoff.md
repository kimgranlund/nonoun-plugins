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

## Acceptance criteria
Run from the repository root. The worktree is uncommitted; judge it with `git diff HEAD` and `git status`.

- T0360-1: `grep '"solo"' plugins/sdlc-lite/adapters/claude/levels.json` prints the solo row with L1 `["sonnet", "low"]`, L2 `["sonnet", "high"]`, L3 `["opus", "xhigh"]`. `git diff HEAD -- plugins/sdlc-lite/adapters/claude/levels.json plugins/sdlc-lite/adapters/codex/models.json` changes only that L2 value (no other row, no models.json change).
- T0360-2: each of these exits 0: `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `bash plugins/sdlc-lite/scripts/run-selftest.sh`, `python3 plugins/sdlc-lite/scripts/evals.py check`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`.
- T0360-3: `.sdlc/evals/0004-solo-l2-high.md` exists with role solo, level L2, model sonnet, effort high, host claude, pass_rate 13/13, the task_set named in the Intent, evidence of both sweep reports, and a Result stating that high matched xhigh on every verdict at 29 to 39 percent of the cost. `.sdlc/evals/table-lock.json` cites it with `previous_eval` `.sdlc/evals/0002-haiku-5-5.md`, and `git diff HEAD` shows the lock written by `evals.py lock` (the sha256 is unchanged because the hash excludes `solo` rows, by T-0342).
- T0360-4: negative control, observed: with `.sdlc/evals/table-lock.json` moved aside, `python3 plugins/sdlc-lite/scripts/evals.py check` exits 1 (`table-lock.json: missing`) and `check.py` reports `FAIL evals`; with the file restored both pass. Changing a non-solo row in a plugin copy (`evals.py --plugin <copy> check`) fails with `model table changed`. Setting solo L2 back to xhigh makes `check.py` fail with `solo levels are not` (a solo row alone does not move the eval hash).
- T0360-5: no live statement that solo L2 is xhigh remains: `git grep -n -E "Sonnet xhigh|sonnet xhigh" -- . ':!docs/reports' ':!docs/other' ':!.sdlc'` prints only `docs/README.md:90` (a dated live-run description, history), and `git grep -n -E "'L2': \('sonnet', 'xhigh'" -- plugins` prints nothing. `agents/solo.md`, `agents/solo-L1.md`, `solo-L2.md`, `solo-L3.md`, `skills/level-rubric/SKILL.md`, `docs/references/sdlc-internals.md`, and `docs/specs/sdlc-lite/solo-lane-contract.md` say Sonnet high for L2, and `agents/solo-L2.md` has front matter `effort: high`.
- T0360-6: scope: `git diff HEAD --name-only` lists only the levels row, its generated agent and Codex files, `check.py`, `fanout.py`, `solo_run.py`, the rubric and the three doc lines, the new eval and the lock, and this handoff; no em or en dash is added outside the generated Codex files (their single-line TOML carries older dashes in unchanged text): `git diff HEAD -- . ':!plugins/sdlc-lite/adapters/codex/agents' | grep '^+' | python3 -c "import sys; print(sum(1 for l in sys.stdin if '\u2014' in l or '\u2013' in l))"` prints 0.

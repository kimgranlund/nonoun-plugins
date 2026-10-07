# Verify T-0352, T-0354, T-0355, T-0358 on main

## Goal
Independently verify four closed solo tickets on main at HEAD (builders were solo sonnet; you are a different family).

## Intent
- Do: for each ticket read its closed folder (.sdlc/.NNNN-*/handoff.md), then check each "Done when" criterion with an observed command in a throwaway copy (git archive HEAD into your tmp prefix; no worktrees). Tickets: T-0352 (dispatch.py record error stdin and solo row), T-0354 (dispatch.py prepare --routing-reason and docs), T-0355 (solo_run.py dispatch file accepted by dispatch.py record), T-0358 (solo role brief stops early when already fixed; positive and negative control evidence).
- Non-goals: editing anything; model or effort changes.
- Done when:
  - A pass or fail per ticket with the command and output for each criterion, and a red control where a criterion is a guard.

## Context
Tickets T-0352 and T-0354 merged via fix0213, T-0355 and T-0358 via solo2. Selftests and check.py passed at merge.

## Constraints
Read-only. No em or en dashes.

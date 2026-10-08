# Verify T-0288 and T-0360 on main

## Goal
Independently verify two closed solo tickets on main at HEAD (builders were solo sonnet; you are a different family). T-0288 retires the Claude headless execution path (breaking, will ship as 0.22.0). T-0360 drops solo L2 from sonnet xhigh to high with an eval lock (user authorized exactly that row).

## Intent
- Do: for each ticket read its closed folder (.sdlc/.NNNN-*/handoff.md), then check each Done-when criterion with an observed command in a throwaway copy (git archive HEAD into your tmp prefix, git-initialised; no worktrees), with a red control where a criterion is a guard. Also confirm T-0360 changed no other levels.json row and no other model or effort anywhere, and that no consumer-facing doc still says solo L2 is xhigh or that Claude headless is the default.
- Non-goals: editing anything.
- Done when: a pass or fail per ticket with the command and output per criterion.

## Context
T-0288 Done-when:
  - `SDLC_BACKEND=claude run.sh builder L1 <handoff>` exits 2 with one line pointing to `dispatch.py prepare` unless `SDLC_CLAUDE_EXEC=1` is set (legacy, bench and CI only), and `run-selftest.sh` covers both with the legacy path still passing.
  - `fanout.py` has no default `claude -p` driver; `--driver CMD` still works; the selftest passes.
  - `check.py` guards that named `claude -p` in the runner are updated (items 4, 20, 21, 27), each with its negative control; `bash plugins/sdlc-lite/scripts/check.sh` passes.
  - `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/AGENTS.md` describe sub-agent mode as the Claude mode and run.sh as the Codex and legacy runner.

T-0360 Done-when:
  - `grep '"solo"' plugins/sdlc-lite/adapters/claude/levels.json` shows L2 as ["sonnet", "high"]; check.py, claude_roles.py generate --check, codex_roles.py generate --check, run-selftest.sh, evals.py check, tickets.py check pass.
  - A negative control: with the eval lock removed or stale, evals.py check fails (observed).

## Constraints
Read-only. No em or en dashes.

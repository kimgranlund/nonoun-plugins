---
id: T-0354
title: "Documented dispatch.py prepare form starts with an env assignment and misses a Bash(python3:*) allowlist, so a headless conductor is denied"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The documented way to run dispatch.py prepare works under a `Bash(python3:*)` allowlist, so a headless conductor is not denied.

## Intent
- Do: Verifier finding F4 of T-0353 (.sdlc/verify-haiku55/verdict.md). The conductor and launcher skills document `SDLC_ROUTING_REASON="<why>" python3 .../dispatch.py prepare ...`; a command that starts with a variable assignment does not match `Bash(python3:*)`, so a headless run was denied twice and spawned nothing. Add a `--routing-reason "<why>"` flag to `dispatch.py prepare` (the env var stays as a fallback), change the documented form in the conductor agent and the skills that name it, and keep the hook and `check.py` guards green. Also: `.claude/settings` examples or the permission-prompt docs in docs/references/claude-hooks.md name the allowlist entries a headless conductor needs; list them.
- Non-goals: model or effort changes.
- Done when:
  - A selftest runs prepare with `--routing-reason` and reads the same routing reason as the env var; a grep shows no skill or agent still documents the env-prefix form (observed failing first).
  - check.py, tickets.py check, dispatch selftest, both generate --check pass.

## Context
Found by the T-0353 verification pass on 2026-10-07 (first headless attempt denied on this exact command).

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: Merged via fix0213 (9a640eb6); verified pass in .sdlc/verify-fix0213/verifier-L3.md

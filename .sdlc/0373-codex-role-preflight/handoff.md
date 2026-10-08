---
id: T-0373
title: "Codex dispatch readiness does not check roles loaded in the current session"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0372]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Before a Codex lane is declared ready, the parent knows the lane's exact role is callable in this session, not only installed, and recovery says what is missing.

## Intent
- Do: A parent-side readiness procedure (skills/sdlc-lite/SKILL.md, adapters/codex/instructions.md, scripts/codex_roles.py, agents/solo.md, skills/agent/SKILL.md, the Codex activation and handoff flow): compare the selected lane's exact role with the host-provided callable agent catalog before claiming or starting work. If a shell script cannot inspect that catalog, the procedure requires the parent to supply or check it; do not invent a host introspection API. Check generated definitions separately with `codex_roles.py install --check` and keep its refusal to overwrite user edits. Name the exact missing role and whether generation, a fresh session, or a launcher repair is required; installation success never implies live availability. Add a concise resume packet (ticket path, conductor-approved base and scope, claim and run state, unresolved launcher issues, mailbox ownership and continuation) so a new session does not create duplicate receiver workers or replay completed replies. Never silently substitute a builder, fall back to Claude, or launch nested Codex CLI. Check the actual native solo transport before reporting that a restart alone unblocks the build (T-0372). Builds after T-0372.
- Non-goals: model or effort changes; hot-reloading the Codex host's agent catalog; launching nested Codex CLI in a live Codex session; silently substituting another role or falling back to Claude.
- Done when:
  - Tests with fixture catalogs: current definitions plus a stale live catalog, stale definitions plus loaded older roles, and a fresh session with the required role available; the first two must not report ready (observed failing first).
  - The readiness text and resume packet are in the Codex adapter and the skill, and `codex_roles.py install --check` behavior is unchanged.
  - check.py, tickets.py check, codex_roles.py generate --check, run-selftest.sh and codex-selftest pass.

## Context
Codex report from the maison repo, 2026-10-08, SDLC Lite 0.21.3, P1: [full report](../../docs/reports/2026-10-08-codex-report-role-preflight.md). A Codex session had builder, planner, verifier and messenger roles but no solo role; steps.py lane returned solo for an L2 ticket; `codex_roles.py install . --check` exited 2 listing the missing solo definitions; `install .` succeeded (28 project agents) but did not add solo to the live catalog. A fresh-session load has not been tested. Mailbox issues are T-0282 and T-0283 in maison and T-0369 to T-0371 here; do not duplicate them.

## Constraints
No em or en dashes. No push or publish. The Codex host cannot be run live here, so a claim about live Codex behavior is marked unverified in the record.

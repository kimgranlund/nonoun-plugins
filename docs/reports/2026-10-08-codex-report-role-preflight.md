---
id: T-0285
title: "Codex dispatch readiness does not check roles loaded in the current session"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket
budget_usd: 30
---

## Intended owner and scope
SDLC Lite author. Local upstream report requested by the user, observed with SDLC Lite 0.21.3 on 2026-10-08. This is a readiness and recovery gap, not a claim that the Codex host must hot-reload agent definitions.

## Problem
A Codex session exposed the SDLC builder, planner, verifier and messenger profiles but none of the solo profiles. The default L2 ticket routing selected solo. The missing capability was discovered only when the user asked to start the build after dispatch and communication setup had been completed.

## Reproduction and observed evidence
1. Open a Codex session whose loaded native agent catalog predates the solo profiles.
2. With the current plugin, run steps.py lane against an L2 ticket. T-0278 returned solo.
3. Inspect the live agent catalog: sdlc-builder-l1 through l5 are available, but sdlc-solo-l2 is absent.
4. codex_roles.py install . --check returned exit 2 and listed missing/stale definitions, including all three solo profiles. The project had no sdlc-solo files before repair.
5. codex_roles.py install . succeeded: Installed 28 project agents; start a fresh Codex session. This did not add solo to the current live tool catalog.

The session stopped before claiming a ticket, creating a lane or changing source. These are observed session facts; a fresh-session load has not yet been tested. Related but independent launcher failure: T-0284.

## Expected
At activation or before declaring a lane ready, distinguish installed plugin version, generated project definitions, and roles actually callable in this session. Identify the exact missing role and state whether generation, a fresh session, or a launcher repair is required. Installation success must not imply live availability.

## Source pointers
skills/sdlc-lite/SKILL.md, adapters/codex/instructions.md, scripts/codex_roles.py, agents/solo.md, skills/agent/SKILL.md and the Codex activation/handoff flow.

## Acceptance criteria
1. A parent-side readiness procedure compares the selected lane's exact role with the host-provided callable agent catalog before claiming or starting work. If a shell script cannot inspect that catalog, explicitly require the parent to supply or check it; do not invent a host introspection API.
2. Check generated definitions separately with codex_roles.py install --check. Preserve its refusal to overwrite user edits.
3. Test current definitions plus stale live catalog, stale definitions plus loaded older roles, and a fresh session with the required role available. The first two must not report ready.
4. Recovery gives a concise resume packet: ticket path, conductor-approved base/scope, current claim/run state, unresolved launcher issues, and mailbox ownership/continuation. A new session must not create duplicate receiver workers or replay completed replies.
5. Check the actual native solo transport before reporting that restart alone unblocks the build, including the failure in T-0284.
6. Never silently substitute a builder, fall back to Claude, or launch nested Codex CLI to conceal missing roles.

## Impact and mitigation
T-0278 could not launch in this session. Managed definitions have been refreshed and Claude was notified; no build has started. A fresh session is needed for role loading, and T-0284 also needs a supported launcher fix. Existing mailbox issues remain in T-0282/T-0283 and should not be duplicated here.

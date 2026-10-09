---
id: T-0389
title: "Codex readiness distinguishes a callable role name from the loaded profile revision"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A Codex lane is not reported ready on a callable role name alone: the role reports the profile revision it loaded before it edits, the parent compares it with the attempt binding, and a mismatch is refused with a fresh-session action or the status is `live freshness unknown`.

## Intent
- Do: extend the Codex readiness procedure from T-0373 (adapters/codex/instructions.md "Readiness and resume for conductors", scripts/codex_roles.py, agents/solo.md, skills/agent/SKILL.md): generated role definitions carry a fingerprint (plugin version and a hash of the generated profile), the role's first report line states the fingerprint it loaded, and the parent compares it with the attempt's binding before accepting any edits; a mismatch is refused with the instruction to start a fresh Codex session (install does not change a running session). If the host exposes no runtime fingerprint, the status is `unknown` and an explicit handshake is required; never claim ready. Also ask whether the stale profile explains the T-0287 (maison) missing formal red-checkpoint rows: T-0378 shipped procedural red-checkpoint rows, and a builder running a pre-0.22 profile would not write them; record the answer in the ticket.
- Non-goals: model or effort changes; inventing a host introspection API; patching installed caches.
- Done when:
  - Fixture tests (observed failing first): loaded fingerprint equals binding -> ready; differs -> refused with the fresh-session action; absent -> `unknown` and handshake required.
  - codex_roles.py install --check behavior is unchanged; check.py, tickets.py check, codex-selftest, both generate --check pass.

## Context
Codex evidence forwarded by the maison conductor, 2026-10-08 (maison .sdlc/tickets/0285-codex-role-preflight/live-profile-version-gap-2026-10-08.md): after installing 0.22.0 a Codex session kept its older native role catalog; new worktrees had fresh 0.22.0 definitions and preflight returned ready, yet the T-0298 and T-0303 step-1 builder reports still tried the removed 0.21.3 results.py, because the role instructions were loaded earlier. Not a missing role or wrong request base. Maison also reports two recurrences already ticketed here: T-0378 (formal red-checkpoint rows missing) and T-0371 (stray worktree warnings for sibling lanes created by the parent; ask maison for the exact text and version, since it may still be on 0.21.x for that path). The Codex host cannot be run here; mark live behavior unverified.

## Constraints
No em or en dashes. No push or publish.

## Result (solo, 2026-10-08)
- Built: each generated Codex profile ends with a fingerprint (plugin version plus a 12 hex hash of name, model, effort, sandbox and instructions) and tells the role to put `profile: <fingerprint>` on the first line of its first message and final report before any edit. `codex_roles.py fingerprint <role>` prints the binding; `codex_roles.py handshake <role> [--report-file f] [--binding fp]` exits 0 ready (equal), 2 refused (differs: start a fresh Codex session, install does not change a running one), 3 `live freshness unknown` (none stated: handshake required, never ready). Preflight `ready` now says live freshness is unknown until the handshake. `install --check` logic is unchanged; the generated toml files changed only by the added fingerprint note.
- T-0287 (maison) missing red-checkpoint rows: T-0378 first shipped in v0.22.0 (tag contains it). A builder loaded from a pre-0.22 profile has no instruction to write procedural red-checkpoint rows, so a stale session profile is a sufficient and plausible explanation, the same mechanism as the 0.21.3 results.py report. Unverified: maison's actual loaded version for T-0287 is not in this repo; the fingerprint line in a builder report would confirm it next time.
- Live Codex behavior (a real session honoring the first-line instruction) is unverified; fixture tests only.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py` passes, including the five handshake and fingerprint tests (equal -> ready; differs -> refused with "Start a fresh Codex session"; absent or not-first-line -> `unknown` with "Handshake required").
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `claude_roles.py generate --check`, `plugins/sdlc-lite/scripts/check.py` and `tickets.py --root .sdlc check` pass.
- Every `adapters/codex/agents/*.toml` ends with a `# Profile fingerprint` note whose `profile: <fingerprint>` equals `codex_roles.py fingerprint <name>`.
- `install --check` code path is unchanged (diff of `install` shows no edits); `instructions.md`, `agents/solo.md` and `skills/agent/SKILL.md` describe the handshake.
- The T-0287 answer is recorded in this file.

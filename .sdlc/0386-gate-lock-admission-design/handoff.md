---
id: T-0386
title: "Design review: gate_lock.py as the weighted shared admission authority"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A written design answer for the proposal to extend gate_lock.py into the weighted shared admission authority, with a decision from the maintainer before any implementation.

## Intent
- Do: Review the maison proposal (.sdlc/tickets/0300-shared-resource-lease-design/interface-contract.md, regression-cases.md, author-message.md): one local state namespace per host and OS user across repos and worktrees, atomic vector grants (compute_units and browser_jobs), FIFO within a repo and round robin across repos, authenticated nesting, durable spawn fence and exact process identity, separate wait and execution timing, required mode failing before heavy work. Compare with gate_lock.py as it is (slot count per command under the caller TMPDIR, SDLC_GATE_LOCK_HELD trusted) and with SDLC_GATE_WORKERS. Return an agreed interface or a counter-design with the owner split, in a design document under docs/specs/. The proposed numbers 6 and 3 are NOT approved; calibration comes only from future real runs. Design only; no implementation.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A design document with the interface, what stays repo-side and what is plugin-side, migration for old plugin paths, and the regression cases it must pass.
  - The maintainer's decision recorded here before any build ticket is filed.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Maison proposal 2026-10-08 (T-0300 design spike). Related maison items: T-0298 (Panda process and lock edges), T-0299 (receipt and preflight), and the load false reds in the fleet retro (load 20 to 57, Phase A 76 minutes). Needs the maintainer's agreement: it moves machine-wide scheduling into the plugin. No response is treated as approval. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.

## Decision
Pending: maintainer. Not decided; no build ticket may be filed until this section records the choice. Silence is not approval.

The design is [gate-lock-admission.md](../../docs/specs/sdlc-lite/gate-lock-admission.md). Questions (its section 11):
1. v1 scope: the counter-design (recommended: namespace from the OS account, plugin-owned policy, vector demand, FIFO per repo with round robin across repos, process-group liveness with exact start identity, grant id plus process group nesting, four timings) or the maison proposal as written (adds the start barrier, capability delegation, sibling failure, request UUIDs, quarantine state machine).
2. Client discovery: a stable launcher in the state root (recommended) or another mechanism.
3. Drain a gate's process group before release when its leader exits first (recommended; a behavior change).
4. Keep `SDLC_GATE_SLOTS=0` and `--no-gate-lock` as the explicit, unprotected opt-out (recommended) or remove them.
5. Numbers: the built-in policy keeps today's behavior; 6 compute units and 3 browser jobs stay unapproved until calibration from real runs.

## Acceptance criteria
1. A design document under docs/specs/sdlc-lite/ answers the maison T-0300 proposal: it compares the proposal with gate_lock.py as it is (namespace, per-caller slot count, nesting flag, liveness) and with SDLC_GATE_WORKERS, and states an interface (commands, environment, exit codes, receipt), the plugin-side and repo-side owner split, migration for old plugin paths (legacy slot files, the nesting variable, the check.py item 35 pins, selftest isolation), and the regression cases, with each maison case R01 to R30 marked v1, deferred, repo, or not adopted.
2. The document approves no capacity number: the built-in default reproduces today's two-gate behavior, and 6 and 3 are named as unapproved, pending calibration from real runs.
3. The document marks Codex host behavior unverified.
4. This handoff records the maintainer decision as pending, with the questions and a recommendation, and no build ticket for this design exists.
5. Only documentation and this ticket change: no file under plugins/ or scripts/ differs from the base commit.
6. The changed and added files contain no em or en dash.
7. `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/tickets.py check`, `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/onboard.py selftest`, `python3 plugins/sdlc-lite/scripts/docs_check.py` and `git diff --check` pass; `onboard.py check` reports nothing stale or unmanaged beyond what it reported before this change (AGENTS.md unmanaged, docs/references/AGENTS.md stale).

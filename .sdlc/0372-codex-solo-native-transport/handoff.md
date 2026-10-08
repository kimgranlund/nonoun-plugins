---
id: T-0372
title: "Codex solo launcher does not supply the native exchange request file"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A Codex solo run through the native subagent transport creates the exchange request, waits for the parent result, and records the correct backend and transport.

## Intent
- Do: Fix scripts/solo_run.py (command() builds codex_exec.py solo L2 <brief> without --request-file; main() sends the Codex backend through run() while its dispatch_json path is Claude-specific; build_record() labels every Codex run transport as exec) and scripts/codex_exec.py (run() requires request_file for the subagent transport; only conductor has an automatic request-file fallback) so solo gets the same native request lifecycle as conductor. Preserve standalone exec mode for its supported callers. Update skills/agent/SKILL.md, agents/solo.md and the Codex adapter text with one runnable invocation and the completion sequence, including report capture and cleanup.
- Non-goals: model or effort changes; hot-reloading the Codex host's agent catalog; launching nested Codex CLI in a live Codex session; silently substituting another role or falling back to Claude.
- Done when:
  - A no-model integration test starts solo with backend codex and transport subagent, observes a valid request file, submits a fixture response through scripts/codex_exchange.py, and completes with an accurate run record (observed failing first; repro in docs/reports/2026-10-08-codex-report-solo-native-transport/repro.json).
  - It covers solo L1, L2 and L3 routing, response failure, timeout, and a rerun request name that does not overwrite an earlier attempt, and it fails when the request-file wiring is removed (assert the request lifecycle, not only command construction).
  - The native record says backend codex and transport subagent; unknown cost is null with a reason; no Claude model, agent name or nested codex exec appears.
  - check.py, tickets.py check, codex_roles.py generate --check, run-selftest.sh and codex-selftest pass.

## Context
Codex report from the maison repo, 2026-10-08, SDLC Lite 0.21.3, priority P1 (it blocks maison T-0278): [full report](../../docs/reports/2026-10-08-codex-report-solo-native-transport.md) and [repro](../../docs/reports/2026-10-08-codex-report-solo-native-transport/repro.json). Reproduce with SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent solo_run.py run --backend codex --task-dir <ticket> --tier L2 --no-worktree in a temp dir: exit 2, `Codex execution failed: subagent transport requires --request-file`, no request file, an unsuccessful attempt recorded. Related: T-0373 (role readiness), and the maison tickets T-0282 and T-0283 for the mailbox.

## Constraints
No em or en dashes. No push or publish. The Codex host cannot be run live here, so a claim about live Codex behavior is marked unverified in the record.

---
id: T-0284
title: "Codex solo launcher does not supply the native exchange request file"
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
SDLC Lite author. Local upstream report requested by the user; not authorization to modify the installed plugin cache or Maison implementation. Observed in Codex with SDLC Lite 0.21.3 on 2026-10-08.

## Problem
The default solo L2 lane cannot start through the documented Codex native-subagent transport, even if the exact native role is available. This independently blocks T-0278 after its role-registration problem is resolved.

## Reproduction
In a temporary directory outside a Git checkout, create ticket/handoff.md with a minimal L2 ticket. Run:
```sh
SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent python3 "$PLUGIN/scripts/solo_run.py" run --backend codex --task-dir "$TMP/ticket" --tier L2 --brief 'Transport probe, no implementation' --cwd "$TMP" --no-worktree
```
Set PLUGIN to the installed SDLC Lite root and TMP to the disposable directory. No model invocation is needed. Captured actual arguments, output and exit code are in [repro.json](2026-10-08-codex-report-solo-native-transport/repro.json).

## Actual
Exit 2. stderr: `Codex execution failed: subagent transport requires --request-file`. No native request file is written; the wrapper records an unsuccessful solo attempt in runs.jsonl. No Codex CLI or native agent starts.

## Cause and source pointers
- scripts/solo_run.py command() constructs codex_exec.py solo L2 <brief>, without --request-file.
- scripts/codex_exec.py run() requires request_file for subagent transport. Only conductor has an automatic request-file fallback.
- solo_run.py main() sends the Codex backend through run(); its dispatch_json path is Claude-specific.
- solo_run.py build_record() labels every Codex run transport as exec, which also needs correction when native transport is wired.
- agents/solo.md says to use the existing Codex role path, but the generic runner exchange instructions do not give a complete solo-specific command and lifecycle.

## Expected
A documented Codex solo command creates a native exchange request for the exact sdlc-solo-l2 role, waits for the parent to submit its actual result, records the correct backend/transport, and releases the waiting process. Preserve standalone exec mode for its supported callers; do not work around this by launching nested Codex CLI in a live Codex session.

## Acceptance criteria
1. A no-model integration test starts solo with backend codex and transport subagent, observes a valid request file, submits a fixture response through codex_exchange.py, and completes with an accurate run record.
2. Cover solo L1, L2 and L3 routing, response failure, timeout, and rerun request naming without overwriting earlier attempts.
3. The test fails when request-file wiring is removed. Assert the request lifecycle, not only command construction or mocked codex output.
4. Native records say backend codex and transport subagent; unknown cost is null with a reason. No Claude model, agent name, or nested codex exec is used.
5. Update the solo skill/role and Codex adapter with one runnable invocation and completion sequence, including report capture and cleanup.

## Workaround and limits
No supported live-session workaround was established. Installing roles and restarting resolves a separate role-availability problem only. The temporary reproduction did not modify application source or dispatch a model.

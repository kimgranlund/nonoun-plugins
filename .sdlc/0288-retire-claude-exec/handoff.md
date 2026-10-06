---
id: T-0288
title: "Retire the Claude headless execution path"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0287]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After the live evidence, the Claude branch of run.sh, the Claude path of solo_run.py, and fanout's headless conductor default are removed or put behind an explicit legacy flag, and run.sh remains the Codex runner.

## Intent
- Do: Retire the Claude headless execution path.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `SDLC_BACKEND=claude run.sh builder L1 <handoff>` exits 2 with one line pointing to `dispatch.py prepare` unless `SDLC_CLAUDE_EXEC=1` is set (legacy, bench and CI only), and `run-selftest.sh` covers both with the legacy path still passing.
  - `fanout.py` has no default `claude -p` driver; `--driver CMD` still works; the selftest passes.
  - `check.py` guards that named `claude -p` in the runner are updated (items 4, 20, 21, 27), each with its negative control; `bash plugins/sdlc-lite/scripts/check.sh` passes.
  - `docs/maintenance/sdlc-internals.md` and `plugins/sdlc-lite/AGENTS.md` describe sub-agent mode as the Claude mode and run.sh as the Codex and legacy runner.

## Context
Design section 8. Do not start before the live-evidence ticket is closed with a pass.

## Constraints
No push, tag, or publish; release notes only if the user asks. No em dashes. No push, tag, or publish.

---
id: T-0092
title: "Run a live probe to confirm that the running Claude Code version..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0076
---

## Goal
A repeatable live probe proves, against the installed Claude Code version, that the subagent tool reaches PreToolUse as `tool_name` `Agent` (so the `"matcher": "Agent"` entry in plugins/sdlc-lite/hooks/hooks.json fires), that `hooks/block-background.sh` denies an Agent call with `run_in_background` missing or `true` under `SDLC_HEADLESS=1`, and that an Agent call with `run_in_background: false` is accepted by the tool schema and passes the hook. The probe is run once live and its result recorded in the task dir.

## Context
Follow-up from T-0076 (headless-conductors-can-still-abandon/filer-L1.md):

Run a live probe to confirm that the running Claude Code version reports the subagent tool as `Agent`, not `Task`, in PreToolUse `tool_name` and matchers, and that `run_in_background: false` is accepted. If either fails, the new block-background.sh Agent guard never fires or blocks every headless Agent call.

## Constraints
- Extend the existing opt-in `plugins/sdlc-lite/scripts/hook-live-probe.sh` (or add a mode to it) rather than a new tool; `scripts/check.sh` keeps running only its offline `--selftest` (stub claude, no model call), and the selftest must cover the new Agent path.
- Live runs use a cheap model (default haiku) and at most a few model calls; exit codes stay 0 PASS, 1 FAIL, 2 setup error.
- The existing Bash probe behavior and CLAUDE.md / sdlc-lite-author.md descriptions stay accurate (update them in the same change).
- If the live probe shows the tool name is `Task` or `run_in_background: false` is rejected, record that as the finding; do not silently change hooks.json in the same step.
- Never commit, push, or publish.

## Plan review
- step 2 builder L1 blocked: plan defect: `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/hook-live-probe.sh` cannot pass because step 1 (verified pass) left hook-live-probe.sh modified and uncommitted; steps never commit. The live probe already ran and PASSed; its output is in .sdlc/0092-run-a-live-probe-to/agent-probe.md (keep it, do not rerun the model unless needed).
- step 3 split --only 3 refused: guard `bash plugins/sdlc-lite/scripts/check.sh` timed out at the default 300s (it takes 7 to 15 min here, not red). Resplit with --guard-timeout 3000: all guards green.

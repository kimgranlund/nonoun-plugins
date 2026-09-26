---
id: T-0075
title: "Confirm with a live claude -p probe that the Bash PreToolUse..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0072
---

## Goal
Evidence from a real `claude -p` session, not a fixture, of the exact JSON shape Claude Code sends a PreToolUse(Bash) hook when the model calls Bash with `run_in_background: true` (field path `tool_input.run_in_background`, JSON type boolean), and proof that `hooks/block-background.sh` denies that live call when `SDLC_HEADLESS=1`. If the live shape differs from the fixtures, fix the hook and the fixtures in `scripts/hook-selftest.sh` to match.

Done when: a repeatable probe script exists (for example `scripts/hook-live-probe.sh`, opt-in, never run by `check.sh` because it spends a model call), it has been run once with its captured payload and verdict recorded in the task dir, and `scripts/check.sh` stays green. (Clarified by the conductor, unattended.)

## Context
Follow-up from T-0072 (headless-background-abandon/filer-L1.md):

Confirm with a live `claude -p` probe that the Bash PreToolUse payload carries `tool_input.run_in_background` as a JSON boolean. `block-background.sh` is proven only against fixtures, so a different field shape would silently disable it.

## Constraints
- `scripts/check.sh` must not start calling a live model; the probe is opt-in.
- The probe must not change any hook behavior for interactive sessions, and must clean up any temp settings, plugin dir, or files it creates.
- Keep the probe cheap: one short `claude -p` call on a small model (for example `--model haiku` or sonnet), bounded by a timeout.
- Docs that describe hooks or selftests (this plugin's CLAUDE.md layout notes, `.claude/agents/sdlc-lite-author.md`) stay in sync if a new script is added.

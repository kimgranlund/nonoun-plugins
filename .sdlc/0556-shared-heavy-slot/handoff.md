---
id: T-0556
title: "Heavy checks a role runs inside its lane go through gate_lock.py"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
branch: lane/T-0556-w72-0556
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Heavy checks a role runs inside its lane (heavy suites, browser tests, the full `check.sh`) go through the plugin's machine-wide queue `scripts/gate_lock.py`, as fanout `--gate` commands already do, so parallel lanes across repos cannot overload the machine.

## Intent
- Do: one short rule in `agents/builder.md`, `agents/solo.md` and `agents/verifier.md`: heavy suites, browser tests and the full `check.sh` run as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gate_lock.py" run -- <cmd>`; the same line in `skills/fanout/SKILL.md`.
- Do: regenerate the agents with `claude_roles.py generate` and `codex_roles.py generate`.
- Non-goals: a second limiter (no `slot.sh`, no `heavy_slots:` key; `gate_lock.py` already caps, queues and reclaims crashed holders); replacing a repo's own test runner; scheduling across machines.
- Done when: both `generate --check` and `check.py` pass, `gate_lock.py selftest` passes, and the rule greps in each of the four files.

## Context
2026-10-14: load average 54 on 20 cores. gen-ui-kit's `gate_lock` is this plugin's `scripts/gate_lock.py`; maison's `.sdlc/browser-slot.sh` is a separate repo-local limiter that can delegate to it. The gap: only fanout `--gate` commands were wrapped, so heavy checks a solo, builder or verifier ran inside a lane (as in `adia/ui-kit`) bypassed the queue.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- [ ] `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- [ ] `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0.
- [ ] `grep -c 'gate_lock.py" run -- <cmd>' plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/solo.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/skills/fanout/SKILL.md` prints 1 for each file.

## Constraints
Ships in 0.23.0 (maintainer, 2026-10-14). The failing selftest lands before or with the change.

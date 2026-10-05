## Goal
Independent check that branch `plan-reviewer-role` delivers T-0171: a plan-reviewer role that rejects a defective plan before a builder starts, on Claude Code and Codex.

## Context
Ticket record: `.sdlc/.0171-plan-reviewer-role/handoff.md`. Live evidence: `docs/reports/plan-reviewer-live-run.md`. Decisions: the ticket's Decisions section. The change touches `scripts/run.sh`, `scripts/steps.py`, `scripts/order.py`, `scripts/check.py`, `scripts/codex_roles.py`, `agents/plan-reviewer.md`, the planner and skills, `adapters/codex/models.json` and the generated Codex agents.

## Constraints
Read-only. No commit, push, or publish.

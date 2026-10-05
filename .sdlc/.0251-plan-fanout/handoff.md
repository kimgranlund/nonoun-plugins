---
id: T-0251
title: "plan-fanout skill"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The /sdlc-lite:plan-fanout skill returns the exact `fanout.py run` command with a dry run first, which passes plan_check.py fanout and which fanout.py --dry-run accepts.

## Intent
- Do: skills/plan-fanout/SKILL.md plus references; flags from fanout.py's real parser (lanes <lane>=<id>[,<id>...], --max-lanes default 4 and above 16 needs --yes-many, --stagger default 20, --lane auto|solo|full, --allow-overlap, --gate, --integration, --base, --lanes-dir, --dry-run, SDLC_BACKEND for Codex); group tickets into lanes by estimated file overlap (planned scope exists only for planned tickets; solo tickets have none, so estimate from paths cited in the ticket), one writer per file, dependent tickets ordered in one lane, lane count within cap and plan limit, budgets (S $5, M $30, L $60), gates, merge order and conflict hot spots (check.py guard numbers, check.sh, root AGENTS.md, docs/README.md, router blocks); when NOT to fan out.
- Non-goals: running /goal or /loop (they cannot run headlessly); model or effort defaults; a version bump, tag, push, or publish.
- Done when: the skill, validator (shared in T-0249), guard and routes exist, the plan_check selftest passes with a negative control per rule, and the batched L3 verifier passed.

## Context
User request: 'plan and create skills for planning fanout, goal, and loop sessions: /plan-fanout, /plan-goal, /plan-loop ... return a compliant copy/paste format for user to input and execute'. Built together on branch plan-skills with one batched verifier. Philosophy: "Done is better than perfect."

## Constraints
No harness: references; Codex adapter line; one authoritative place per fact. No em dashes.

## Closed

2026-10-05: built on branch plan-skills; verified by one L3 Fable verifier; see docs/validation/plan-skills-live-run.md

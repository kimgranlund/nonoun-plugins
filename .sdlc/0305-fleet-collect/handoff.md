---
id: T-0305
title: "fleet_collect.py: per-repo collector"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A read-only script that turns one repo's run records and the machine state into one JSON fingerprint, with no model call.

## Intent
- Do: Add plugins/sdlc-lite/scripts/fleet_collect.py with `collect <repo> [--since DATE] [--gh] > out.json` and `selftest`. Output keys: env (plugin version path in use, claude version, time, uptime load), runs (cost_usd, duration, count by role and by lane solo vs full, deduped by attempt_id; interrupted and `.limit` marker counts; lane overrides from skips.md), plan_review_share (plan-reviewer plus planner cost over total), processes (counts and CPU of chromium, hooks, claude), worktrees (count, size via bounded du with a timeout), ci (with --gh: runs and wall minutes by workflow via gh api, last N days).
- Non-goals: Detect rules (T-0306), the interview (T-0307), the report (T-0308).
- Done when:
  - `fleet_collect.py selftest` passes on a fixture repo whose runs.jsonl has duplicate attempt_ids and an interrupted attempt: the totals count each attempt once and the interrupted one is reported (observed negative control: duplicates change the total if dedupe is disabled).
  - Run on /Users/kimgranlund/Projects/nonoun/agent-ui prints a total that matches its own report's 193 deduped runs within 2 percent, and prints it without writing any file in that repo (git status unchanged).
  - A repo with no .sdlc exits 0 with `runs: none` and does not crash.
  - `du` on a huge worktree directory times out cleanly and says `size: unknown` instead of hanging.
  - `check.py` and `tickets.py check` pass.

## Context
Decided by the user on 2026-10-06 after three repo root-cause reports (maison, agent-ui, gen-ui-kit, each at root-cause-2026-10-06.md in its repo). Design: a thin skill `/sdlc-lite:fleet-retro` on top of the existing `review-traces` skill: a deterministic collector, mechanical detect rules, a 5-question conductor interview, one cross-repo ranked report, a sampled verifier, then filing through review-traces. Existing pieces to reuse: runs.jsonl dedupe by attempt_id (agent-ui's method), scripts/budget.py cost sums, skills/review-traces/SKILL.md, scripts/footprint.py. Build after the 0.20.11 batch ships; target release 0.21.1.

## Constraints
No model call inside collect or detect. Read-only on every repo it inspects. No em dashes. No change to any model or effort value. No push, tag or publish.

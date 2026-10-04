---
id: T-0199
title: "Conductor batching and skip rules"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0196, T-0198]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Write the conductor batching and skip rules, using the lane script, batched verification, and skips.md.

## Intent
- Do: Section 4 of the design: run `steps.py lane` and follow it; batch plan reviews across a fanout run on one model family; use whole-ticket verification for independent steps only at builder levels where per-step verification is not mandatory; one `/open-questions` round per ticket set; parallelize independent tickets in fanout lanes; record every skip in `skips.md`; the lean lane always runs the filer (resolved decision 2). A skip the lane script does not permit needs the user's approval through AskUserQuestion before it is recorded, at every size (author default; the user may change it). Never skipped: the independent verifier on L4 or L5 and merge steps, the required plan review, a focused live run for a role behavior change, the filer when follow-ups or warnings were reported, user approval for any publish.
- Also do (objective and lane gravity, user decision 2026-10-04, from the conductor-pull discussion): (a) conductor.md opens with the project philosophy, quoted exactly, "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction.", and then one objective line: the job is the cheapest path that still passes independent verification, and the lane is chosen before any role runs. (b) "Route every ask" puts the lane decision first: size S to /fix, size M to the lean lane (one or two steps, planner L2), the full chain only with a stated reason (L4 or L5 step, merge step, cross-cutting scope, security-sensitive change); escalating to a heavier lane is what needs justification. (c) Before dispatch the conductor writes one line, `Lane: <lane> because <reason>`, and the same line is recorded in the ticket or task folder. (d) The stop rules are the conductor's own: a second replan verdict, or a ticket past its budget when the cost-control budget ticket lands, is a hard stop that comes to the user. Keep conductor.md short (it is read every turn); put detail in the lane script's output, not in prose. check.py guards each of (a) to (d) with a negative control. Do not edit the repository or plugin AGENTS.md invariants here; the maintainer-side line is a separate ticket.
- Also do (thin conductor, user decision 2026-10-04 after reading docs/other/orchestration-optimization-question.md): (e) one more conductor rule: delegate context-heavy reads and long checks to a role or read-only agent and take back conclusions, not file contents or logs; do not narrate every background wake-up; keep the conductor's own context small because it persists and every later turn pays for it. (f) extend scripts/footprint.py (T-0193, merged) with an optional `--session <transcript.jsonl>` that reports the conductor session's token usage (input, cache read, output) next to the task's role costs, with a selftest and a negative control (a transcript with no usage lines reports none, not zero cost). check.py guards (e) with a negative control. Keep it small.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L7), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0192 (conductor batching), which is closed in favor of these tickets. Depends on: T-0196, T-0198. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/agents/conductor.md, plugins/sdlc-lite/skills/chain/SKILL.md, plugins/sdlc-lite/skills/fix/SKILL.md if affected, check.py guards, regenerated Codex agents.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Do not edit the repository and plugin AGENTS.md invariants. check.py guards with negative controls for the new text. `codex_roles.py generate --check` passes. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Closed

2026-10-04: Built via one handwritten L3 step; verifier L2 pass; gates green. Burn-down: no planner, no filer, one verifier.

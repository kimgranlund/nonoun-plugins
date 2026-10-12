---
id: T-0460
title: "Build /sdlc-lite:report: scripts/report.py and the skill (executive summary, views, health signals, hygiene grade)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L4             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:report` prints a short executive summary of the current agent thread by default, and the named views (tasks, signals, needs, context, cost, children, identity, evidence, full) on request, from records and the transcript, with no model call in the collector.

## Intent
- Do: build `plugins/sdlc-lite/scripts/report.py` (`collect`, `render`, `selftest`) and ship the skill at `plugins/sdlc-lite/skills/report/SKILL.md` with `references/views.md` and `references/record-schema.md`, starting from the maintainer-approved drafts in `.sdlc/0460-report-skill/draft/` (copy and adjust; the draft SKILL.md is the contract for behavior, views, options, refusal and rules). Implement in two stages inside this one build. Stage 1, records only: identity, state (pid liveness, time since last activity), work, timeline (`recent` from closed tickets and passed verifier results, `now` from the open attempt and `steps.py next`, `next` from `depends:` and the ready queue with `planned` or `intended`), cost (`runs.jsonl`, `budget.py`, priced versus unpriced), needs, and the records-only health signals (late failure, trivial last failure, rework, stall, gate wait, retries, dead-end work). Stage 2, transcript: peak context fill, compactions, re-reads, read-to-use, exploration, workaround chains, noisy output, read from the session transcript `usage` and tool calls the way `dispatch.py record --transcript` already reads usage. Views and options exactly as in the draft; an unknown view or option is refused (exit 2) listing the valid ones; `--format json` returns the `session-status/1` record; one snapshot is stored under `.sdlc/runtime/report/` unless `--no-snapshot`; `--compare last` marks changes; `--explain` prints rule, value and threshold; thresholds come from `.sdlc/config` keys with the draft's starting values, every flag `[U]` until calibrated; the grade band (A to D) names the flags that set it.
- Controlled language: entries use the closed verb list and tense rule of `docs/specs/doc-standards/core.md` (add the verb list and the tense rule there and to `docs/references/glossary.md` in this build); a verb outside the list is a collector error; `next` never contains an item with no ticket or step unless marked `intended`; unknown values are listed under `unknown`, never shown as 0.
- Checks: a selftest on a fixture repo and a fixture transcript with an observed-red control per rule (a dead pid reads `dead`, a long quiet period reads `stalled`, an unreadable cost appears in `unknown` and not as 0, an unknown view is refused, a verb outside the list is rejected, a 4-turn late failure fixture flags late failure, a fixture with 3 re-reads flags re-reads); wire the selftest into `check.sh`; `check.py` pins the skill phrases (render, never compose; `report.py`; `Codex host`; the refusal) with negative controls; `check-packaging.py` passes; the skill stays self-contained (item 42); add the skill to the routing rows of `skills/sdlc-lite/SKILL.md` and to `plugins/sdlc-lite/AGENTS.md` if it lists scripts or skills.
- Non-goals: reading another session (`--session` stays refused as reserved); changing any role or model row; calibrating thresholds (a later retro does that); Codex transcript parsing (the skill states the Codex mapping as unverified).
- Done when: `python3 plugins/sdlc-lite/scripts/report.py selftest` exits 0 with every control observed red before the rule; `/sdlc-lite:report` run on this repo prints the executive summary in at most 8 lines, `full` prints every section, `--format json` validates against the schema in `record-schema.md`; `check.py`, `check-packaging.py` and `check.sh` exit 0; one live run in this session is recorded in the ticket notes (what it printed, what was `unknown`).

## Context
Design thread: the maintainer's `session-status` request, renamed `report`, with the timeline block (recent, now, next), the health and context hygiene signals, the view and option interface, and the controlled-language rules. Draft files: `.sdlc/0460-report-skill/draft/SKILL.md`, `draft/references/views.md`, `draft/references/record-schema.md`. Existing patterns: `skills/fleet-status` and `scripts/fleet_status.py` (render, never compose), `scripts/fleet_collect.py` and `fleet_detect.py` (fingerprints, evidence pointers), `scripts/dispatch.py` (attempt records, transcript usage), `scripts/steps.py next`, `scripts/gate_lock.py status`, `scripts/budget.py`. Document standards: `docs/specs/doc-standards/core.md`, `prompts.md`. Retro rubric for evidence pointers: `skills/fleet-retro/rubric.md`.

## Constraints
No model call in the collector or renderer. Read-only against the repo except the snapshot under `.sdlc/runtime/`. No model or effort change. State only what a record shows. Hot files (`check.sh`, `check.py`) one writer at a time.

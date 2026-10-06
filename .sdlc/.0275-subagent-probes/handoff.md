---
id: T-0275
title: "Probe the sub-agent mechanics the design assumes"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Observe, in a throwaway project, the eight sub-agent behaviors the design marks unverified, and record each as observed or failed.

## Intent
- Do: Probe the sub-agent mechanics the design assumes.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `docs/reports/subagent-probes-<date>.md` exists with one `| P1 |` to `| P8 |` table row each (8 rows), each row holding raw evidence (a command, a path, or a quoted field), not a summary: `test "$(grep -c "^| P[1-8] |" docs/reports/subagent-probes-*.md)" -eq 8`
  - P1 effort, model, disallowedTools, skills, and permissionMode frontmatter of a plugin-shipped agent are honored (compare a low and an xhigh definition on one task; skills text visible in the sub-agent), and the haiku, sonnet, opus, fable aliases resolve to the pinned models.
  - P2 a plugin PreToolUse hook fires for a sub-agent tool call and its input carries `agent_type` and `agent_id`; `SDLC_ROLE` in the sub-agent env is the parent value; a hook cannot rewrite tool input.
  - P3 the notification usage fields beyond `subagent_tokens`, `tool_uses`, `duration_ms` (already observed), and what a sub-agent that hits a session limit returns.
  - P4 `SendMessage` to a finished named agent resumes it with its transcript; and the same from a new session by id (pass or fail, either is a finding).
  - P5 the sub-agent transcript path and whether `message.model` and per-message usage are readable (feeds verifier independence and cost).
  - P6 a `SubagentStop` hook input: whether it holds the transcript path and last message beyond the documented `agent_id`, `agent_type`, `effort`.
  - P7 the 20-agent limit (`Concurrent subagent limit reached`) is per session or global, and what a parent restart does to background sub-agents.
  - P8 a sub-agent given the Agent tool dispatches a sub-agent (depth 3) and receives its result in the background.
  - Each failed or partly failed probe names the design fallback it triggers (section 9 of the design).

## Context
Design: `docs/lean-sdlc/subagent-mode.md` sections 1 to 9 name each assumption. Run in a scratch repo outside this one; no repo code changes in this ticket.

## Constraints
No runner or hook code changes. No push or publish. No em dashes. No push, tag, or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed

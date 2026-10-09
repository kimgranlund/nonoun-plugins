---
id: T-0399
title: "dispatch.py prepare refuses an unfilled handoff template instead of reaching a verifier"
type: bug             # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare` refuses a handoff that is still the unfilled template, the way it refuses stale input, so no verifier runs on it and reports `fail`.

## Intent
- Do: in scripts/dispatch.py add a prepare gate that detects an unfilled handoff (template placeholder lines such as the `Exact command or steps` or `<...>` stubs the ticket templates ship, and a Goal still reading the template default), exit 2 with one line naming the file and the placeholder, and a `--skip` style bypass only if the existing gate pattern has one. Share the placeholder rule with `tickets.py check` instead of copying it, if it already detects placeholders in closed tickets.
- Non-goals: model or effort changes; changing the verdict vocabulary (T-0400).
- Done when:
  - A dispatch selftest case, observed failing first: prepare on an unfilled template handoff exits 2 naming the placeholder, and prepare on a filled handoff still passes.
  - dispatch.py selftest, check.py and tickets.py check pass.

## Context
Maison and Codex, 2026-10-09: a ticket whose handoff was the unfilled template reached a verifier, which reported fail instead of blocked. Evidence: maison .sdlc/tickets/0301-lean-template-bootstrap-design/codex-progress-bar-stage-evidence.md.

## Constraints
No em or en dashes. No push or publish.

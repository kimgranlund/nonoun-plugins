---
id: T-0299
title: "fanout lane specs accept T-0123 or bare 0123"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py run` accepts `T-0123` or bare `0123` (and `123`) in lane specs and treats them as the same ticket id.

## Context
Maison's bare ids died instantly twice. File: plugins/sdlc-lite/scripts/fanout.py (spec parsing for `<lane>=<id>[,<id>...]`, external `<lane>@<branch>=` too). Normalize to `T-NNNN` at parse time so reports and the twice-listed refusal agree.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with new cases: a dry run with `a=0123` and one with `a=T-0123` resolve the same ticket; `a=0123 b=T-0123` refuses as twice listed.
- [ ] Negative control shown once: without normalization the bare-id case fails.
- [ ] docs/references/sdlc-internals.md fanout entry (or skills/fanout/SKILL.md) says bare ids are accepted.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed

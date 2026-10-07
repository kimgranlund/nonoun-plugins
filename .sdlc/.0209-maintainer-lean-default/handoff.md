---
id: T-0209
title: "Maintainer guidance: prefer the lean lane for plugin work and record why a ticket needs more"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0194]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Plugin maintainers and the author agent default to the cheapest lane that still passes independent verification, and record why a ticket needs more.

## Intent
- Do: add the project philosophy, quoted exactly, "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction.", as the first line of plugins/sdlc-lite/AGENTS.md's guidance (one authoritative location; other files link to it, not copy it), and add one short rule to plugins/sdlc-lite/AGENTS.md (Behavioral invariants or Contracts section): prefer the lean lane or /fix for plugin work, run the full chain only with a stated reason (L4 or L5 step, merge step, cross-cutting scope, security-sensitive change), and record the reason in the ticket. Add the same one-line pointer to .claude/agents/sdlc-lite-author.md if it fits its 9 lines. Also add one completion line to plugins/sdlc-lite/agents/builder.md (shared role body, so run codex_roles.py generate and keep generate --check green): finish the step with the smallest change that meets the criteria; no refactors, extra tests, or doc edits outside the step; report blocked instead of looping. Update the plugin AGENTS.md validation note only if a check guards it. The author agent line itself already shipped in .claude/agents/sdlc-lite-author.md (commit with this ticket edit).
- Non-goals: any other AGENTS.md change; model or effort defaults; a version bump, tag, push, or publish.
- Done when: the line exists in the plugin AGENTS.md, a link check and git diff --check pass, and an independent verifier confirmed it matches the lean design wording.

## Context
Split out of T-0199 because that ticket may not edit AGENTS.md invariants. User decision 2026-10-04 after the discussion of giving burn-down mode more pull at the conductor and author agent level. Depends on the lean lane existing in text (T-0194, merged). Size S: use /fix.

## Constraints
Keep the file short. One authoritative location for the rule; link to docs/lean-sdlc/design.md instead of copying it.

## Closed

2026-10-04: Built and verified through /fix lane: philosophy line and lane rule in plugin AGENTS.md, builder completion line, Codex builder agents regenerated; verifier L1 pass.

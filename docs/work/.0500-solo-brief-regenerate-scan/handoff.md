---
id: T-0500
title: "agents/solo.md: regenerate derived files and scan em dashes and stale counts before verify (retro 12h rows 7 and 8)"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The solo brief tells the builder to regenerate derived files and to scan its diff for em dashes and stale counts before it asks for a verifier, so CI freshness gates and verifier nits do not fail after the substance passes.

## Intent
- Do: add two affirmative lines to `plugins/sdlc-lite/agents/solo.md` `## Loop` step 3, after Run-verbatim: handle `Regenerate`: "Run the regenerate step the repo names for every derived file your diff touches (an index, a manifest, a generated agent) and its freshness check." handle `Scan-diff`: "Scan your added lines for em dashes and for counts or versions in comments your change made stale." Regenerate with `claude_roles.py generate` and `codex_roles.py generate`.
- Non-goals: a lint in `dispatch.py prepare` (a later ticket if the lines do not cut the nits); other wording.
- Done when: a `check.py` item fails when `solo.md` lacks either handle (observed red first); `prompt_lint.py` prohibitions for `solo.md` not above 17; `generate --check` for both hosts and `check.py` exit 0.

## Context
Evidence: `docs/reports/2026-10-12-fleet-retro-12.md` rows 7 and 8: agent-ui, 3 tickets with a verifier fail on an em-dash or stale-count nit after the substance passed (about 15 min each); gen-ui-kit, derived-file freshness gates failed CI 5 times because solo briefs had no regenerate step. Waits for T-0496 only if both edit `solo.md` in the same wave.

## Constraints
One writer on `solo.md`. No model or effort change.

## Closed

2026-10-12: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full

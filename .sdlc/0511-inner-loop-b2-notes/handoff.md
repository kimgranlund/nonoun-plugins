---
id: T-0511
title: "verifier: a Notes section for nits, carried into the close reason (T-0501 B2)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier reports a finding that no criterion names (an em dash in a comment, a stale count or version comment) under `## Notes`, never in the Verdict, and the closer carries the notes into the ticket.

## Intent
- Do: add one affirmative line to `agents/verifier.md` (handle `Notes`): findings that no criterion names go under `## Notes`, one line each with file:line; the Verdict is `fail` only for a red criterion or a defect rule 2 names. Add `Notes` as an optional section of the verifier schema in `results.py` (`validate` keeps order; undeclared headings are already ignored, `:15`). `fanout.py land` composes its close reason (`:941`) to include the notes; `tickets.py close` keeps reading no verifier result. Regenerate with `claude_roles.py generate` and `codex_roles.py generate`.
- Non-goals: a new verdict value (twelve `== 'pass'` readers would change); the T-0496 skip.
- Done when: a `results.py selftest` case with a `## Notes` section validates and a verdict `pass with notes` is still refused (red first for the optional section); a `fanout.py selftest` case shows the notes in the close reason; `check.py` item for the handle observed red; `prompt_lint.py` prohibitions for `verifier.md` not raised; both `generate --check` and `check.py` exit 0.

## Context
Design: `docs/planning/inner-loop-profile.md`. Opt-in by `profile: inner-loop` in `.sdlc/config`; a repo that does not declare it sees no change. Evidence: 4 agent-ui tickets failed only on nits. In T-0075 the nit was a Done-when clause ("records repaired in the same change"), so the verifier failed it by contract: the profile's criteria must not carry nit clauses.

## Constraints
Affirmative wording, no new prohibition. One writer on `verifier.md`.

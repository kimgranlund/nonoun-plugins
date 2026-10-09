---
id: T-0419
title: "Write the standing narrow authorization for managed-block refresh in consumer repos"
type: chore           # feature | bug | chore | spike | idea
status: ready
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
claimed_by: claude 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Conductors may refresh the managed blocks of docs/*/AGENTS.md in their own repo without waiting for the maintainer, under a written narrow rule, and nothing broader.

## Intent
- Do: write the authorization where conductors read it: skills/onboard/SKILL.md and the fleet notes (.sdlc/notes.md plus the conductor text in agents/conductor.md if it states the onboard rule). The rule: a conductor may run `onboard.py check`, then `onboard.py setup --dry-run`, and if the diff touches only `<!-- sdlc-lite:managed:start -->` blocks inside docs/**/AGENTS.md (and the CLAUDE.md pairs) in its own repository, run `onboard.py setup --yes` and commit it; it must never run setup when the dry-run shows the root AGENTS.md, a template change or a new managed file, never `--force` over a hand-edited block, never `tickets.py migrate-size --apply`, and never in another repo. Say what to do otherwise (report to the maintainer with the diff).
- Non-goals: any change to onboard.py behavior; model or effort changes.
- Done when:
  - The rule text exists once in the onboard skill and is linked, not copied, from the conductor text; check.py (self-contained skills, item 42) and docs_check.py pass.
  - A grep shows no other file states the old blanket "never run onboard setup" without pointing at the rule.

## Context
Maintainer decision 2026-10-09: yes to a narrow, written standing authorization (ultimate-tokens' stale managed block warning had waited for hours).

## Constraints
No em or en dashes. No push or publish. Read-only on every consumer repo.

---
id: T-0392
title: "Add docs/goals/ and docs/kpi/ homes with checks, layout and onboard support"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`docs/goals/` and `docs/kpi/` exist as documented, checked homes: a repository that adopts SDLC Lite can write a goal and a KPI in a fixed shape, and `docs_check.py` fails when they are malformed or disconnected.

## Intent
- Do: build the design in docs/planning/goals-and-kpi/design.md (read it first; the user asked for the two homes on 2026-10-08). (1) Add `goals` and `kpi` to `DEFAULT_HOMES` in scripts/docs_check.py and `DOC_KINDS` in scripts/onboard.py, with kinds rows in docs/layout.md (goals: NNN-slug.md, status front matter; kpi: NNN-slug.md, in place) and the matching rows and a "which home" line in the managed Documents block that onboard writes under docs/AGENTS.md (regenerate with onboard's own code path; do not hand-edit managed blocks; do not run `onboard.py setup` against any other repository). (2) Implement checks G-1 to G-5 in docs_check.py exactly as the design's table says, each with a negative control, and a front matter reader that already exists (`front_matter` near line 70). (3) Move the finished design from docs/planning/goals-and-kpi/design.md to docs/specs/repo-onboarding/goals-and-kpi.md, drop its `status: proposed` front matter and the Status line, add the entry-file or index line the D-7 rule needs, and fix links. (4) Add two seed files that exercise the shape and the checks as live examples: docs/goals/001-fleet-load-without-gate-reds.md and docs/kpi/001-runs-without-cost-row.md (ids G-001 and K-001, linked to each other, with a runnable measure from fleet_collect.py and a baseline from docs/reports/2026-10-08-fleet-retro-06.md; mark any value you did not run yourself as unverified). (5) Update skills/onboard text, the fleet-retro skill (outcome metric may cite a KPI id) and the retro rubric C5 note by one sentence each. Keep the design's open choices as defaulted (ids G- and K-, three digits, no stored values, Markdown only).
- Non-goals: model or effort changes; automatic goal-to-ticket generation; a goal ledger in .sdlc; changing any other home.
- Done when:
  - docs_check selftest passes with a positive fixture (valid goal and KPI linked both ways) and a negative control per rule G-1 to G-5, observed failing first.
  - `python3 plugins/sdlc-lite/scripts/docs_check.py` reports 0 errors with the seed files present; removing the KPI file turns G-3 red.
  - onboard.py selftest, check.py, tickets.py check, both generate --check pass; the managed docs/AGENTS.md block lists goals and kpi through onboard's code path.

## Context
User request 2026-10-08: "for sdlc-lite sessions, we should have a place in docs folder for concepts like docs/goals/{###}-{goal-summary-name}.md (or .json) and docs/kpi/{###}-{kpi-summary-name}.md (or .json); elaborate on this a bit and ship it in the next patch". The design elaborates it; JSON is declined for docs/ (rule D-9) and the front matter is the machine-readable part. Target release: 0.22.1.

## Constraints
No em or en dashes. No push or publish. Do not edit another repository.

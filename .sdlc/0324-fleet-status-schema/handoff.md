---
id: T-0324
title: "JSON schema for the fleet_status collect output, and render as one plain aligned CLI table per section"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0323]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The per-repo status that `fleet_status.py collect` emits is pinned by a JSON schema file, and `render` shows it as simple aligned CLI tables (plain columns, one state emoji column), nothing fancier.

## Intent
- Do: (1) Add `docs/sdlc-lite/fleet-status.schema.json` (JSON Schema, draft 2020-12) describing the `collect` object (machine, repos with rows, needs_you, release, delta). The key list already lives in the docstring of plugins/sdlc-lite/scripts/fleet_status.py; make the schema the authority and point the docstring at it. (2) Make `fleet_status.py selftest` validate a collected fixture against the schema using only the standard library (a small checker for the keywords the schema uses; no new dependency) with a negative control (a fixture missing a required key must be rejected). (3) After T-0323 lands, render each section as a plain table: header row, aligned columns padded with spaces, a dashed rule, no markdown pipes, state shown by the colored emoji. If T-0323 chose markdown pipe tables, replace them with this plain form.
- Non-goals: new data fields, the stop line, the skill's AskUserQuestion step, any new dependency.
- Done when:
  - `fleet_status.py collect` output validates against the schema in selftest (observed), and the negative control fails on a missing key.
  - `fleet_status.py render --no-write --no-gh` prints aligned plain tables with no pipes and no em dash.
  - `check.py`, `tickets.py check`, and the fleet_status selftest pass; docs/maintenance/sdlc-internals.md names the schema.

## Context
User direction on 2026-10-06: capture each repo's status in a JSON schema or similar, and show the contents in a simple CLI table. Depends on T-0323 (colored marks, collapse of done-but-open rows).

## Constraints
No em or en dashes. No push or publish. Model and effort defaults unchanged.

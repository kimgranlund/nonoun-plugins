---
date: 2026-10-16
slug: skill-md-restructure
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote the handoff (agent-ui .sdlc/work/fog-skill-restructure/handoff.md) and dispatched the solo
  - role: solo
    agent: sdlc-lite:solo-L2 (fogskill2-solo-L2)
    model: claude-opus-5-5
    did: SKILL.md restructure, references/viewer.md, moved paragraphs into five references, AGENTS.md layout line, this changelog
  - role: verifier
    agent: sdlc-lite:verifier-L2 (fog-skill-restructure-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification, verdict pass; walked the checklist on a real runtime-harness bundle (ingest, validate, publish)
project: agent-ui (nonoun), live round 4 field evidence (a bundle run that stopped at 0 findings)
verification: independent verifier L2 pass (2026-10-16); skill tests 20 of 20
backup: /private/tmp/claude-501/scratch/cfow-backup-1792154787
---

# 2026-10-16: SKILL.md restructure for autonomous runs

SKILL.md went from 179 lines, about two thirds viewer specification, to about 94 lines that lead with the analysis path. No sentence was dropped: a sentence-level coverage check compared every backup SKILL.md sentence against the new SKILL.md plus `references/**/*.md` (370 sentences, 369 present, 1 renamed heading).

## Added
- `SKILL.md`: a routing table first (CLI session trace, runtime-harness bundle, existing v2 `session.json` by diagnose, visualize, compare), an "Autonomous run checklist" ending in the published report id and a cause-classified why-and-fix table ("0 findings is not a result", stop conditions), and a "Prerequisites for detectors" block.
- `references/viewer.md`: the shell's UI specification moved verbatim from SKILL.md (atlas, payload templates, candidate grouping, step-card canvas, indicator strip, focused inspection, canvas navigation and camera, story overview, findings UI and diagnostic focus, sunburst and radial graphs), plus the report library locations and requirements and the post-publish viewer check.

## Changed
- `SKILL.md`: description adds runtime-harness bundles; "Host selection" folded into "Inputs and workflow" with a pointer; hydration steps shortened with pointers; heading "User-level report library" renamed "Report library"; a 4-line "Visual exploration" pointer replaces the viewer sections.
- `references/hydration.md`: new sections "Adapter options and compound reads" and "Context records" (moved from SKILL.md).
- `references/claude.md`: new section "Host selection" (moved from SKILL.md).
- `references/bundles.md`: new section "Folder-based session bundles" (moved from SKILL.md).
- `references/learnings/applying-this-skill.md`: new section "From diagnosis to fixes" (moved from SKILL.md; the checklist now carries its steps).
- `AGENTS.md`: Layout lists `viewer.md`.

## Fixed
- After verification (conductor): checklist step 4 links `references/learnings/triage.md`; the engineering-default line names step 8 as its exception.
- None. No script, asset, schema or test changed.

## Open
- Field-test the checklist on a fresh runtime-harness bundle with an agent that has not seen this ticket.

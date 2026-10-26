---
date: 2026-10-16
slug: runtime-harness-learnings
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote the handoff, the updates-log folder, this changelog and the AGENTS.md change-log line
  - role: solo
    agent: sdlc-lite:solo-L2 (fogskill-solo-L2)
    model: claude-opus-5-5
    did: references/learnings/, AGENTS.md, SKILL.md and cross-link edits, scripts/wrapped.py and scripts/diagnostics.py fixes
  - role: verifier
    agent: sdlc-lite:verifier-L2 (fog-skill-playbook-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification, verdict pass
project: agent-ui (nonoun), live rounds 1 to 5 analyzed with this skill
verification: independent verifier L2 pass (2026-10-16); skill tests 20 of 20
backup: /private/tmp/claude-501/scratch/cfow-backup-1792151864
---

# 2026-10-16: runtime-harness learnings, AGENTS.md, three test fixes

Source: five live rounds on a generative UI runtime harness (agent-ui, rounds 1 to 5, 2026-10-15 and 16), each analyzed with this skill. Requested by Kim; built by a solo agent and checked by an independent verifier (pass). Backup of the skill before these edits: `/private/tmp/claude-501/scratch/cfow-backup-1792151864`.

## Added
- `references/learnings/`: `README.md` (Scope block: these are runtime-harness field lessons, contrasted with a CLI harness; index; lesson format) and seven files: instrument, triage, guidance-authoring, validation-and-repair, test-loop, model-choice, applying-this-skill. 29 lessons, each with a rule, an "Observed in" evidence line, a "Check:" line and an "Applies to:" tag (14 runtime harness, 15 both).
- `AGENTS.md`: layout, where a learning goes and its format, the runtime-vs-CLI rule, the test command, house rules, back up before large edits.
- `updates-log/`: this folder, one dated subfolder per change set.

## Changed
- `SKILL.md`: a 2-line "From diagnosis to fixes" section (triage order, cause classes a to d) linking `references/learnings/README.md`.
- `references/engineering.md`, `references/decision-analysis.md`: one link each to the learnings index.

## Fixed
- `scripts/diagnostics.py`: added `lookup_request` (with `shell_lookup`); `diagnose` uses it instead of a keyword regex, so a `cat > file` write no longer counts as a lookup, and a failed-discovery finding in a compound command needs the error to name a requested target.
- `scripts/wrapped.py`: `cat a b` returns each file read; a Promise batch followed by an ascending indexed `for` loop now parses; result-to-call pairing checks each block's index (a reversed loop is still rejected).
- Tests: `python3 -B -m unittest discover -s tests` went from 12 run with 3 failing (one module failed to import) to 20 run, all passing. No test was edited.

## Open
- The script fixes are proven by unit tests only; run them on a real trace next.

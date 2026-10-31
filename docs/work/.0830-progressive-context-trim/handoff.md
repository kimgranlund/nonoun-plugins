---
id: T-0830
title: "Import the MacBook's 11:33 progressive-context edits (read less, return to the task)"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-31
claimed_by: nonoun-author 2026-10-31
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/context/skills/progressive-context/` carries the five files the user edited on the MacBook on 2026-10-31 11:33 to 11:35, after the T-0829 import, and keeps the one SKILL.md line that links the earlier references.

## Context
- Source, read-only over SMB: `/Volumes/kimba/.codex/skills/progressive-context/` files `SKILL.md`, `references/evaluation.md`, `references/semantic-handoff.md`, `references/review-rubric.md`, `references/tier-model.md`. No other skill on the MacBook changed after 2026-10-31 10:50.
- The edits make the skill read less: start from the task and its authoritative context, open a reference only for an unresolved context mechanism, and treat evaluation, semantic handoff and gap-analysis templates as optional when local checks or formats suffice.
- The repo copy differs from the MacBook only by the SKILL.md line added in T-0829 that links `capability-contracts.md` and six other earlier references; that line must stay.

## Do
1. Copy the five files over the repo copies. Never write to `/Volumes/kimba`.
2. Re-add the earlier-references line to SKILL.md if the copy removed it.
3. Add a context CHANGELOG `[Unreleased]` Changed entry.

## Acceptance criteria
- `for f in references/evaluation.md references/semantic-handoff.md references/review-rubric.md references/tier-model.md; do cmp -s /Volumes/kimba/.codex/skills/progressive-context/$f plugins/context/skills/progressive-context/$f || exit 1; done`
- `grep -q 'capability-contracts.md' plugins/context/skills/progressive-context/SKILL.md`
- `python3 -m unittest discover -s plugins/context/skills/progressive-context/tests` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Outcome

2026-10-31 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: d5f9f4f13c32
- Changed: see commits
- Commits: 954bbc2 T-0830: import MacBook progressive-context trim (read less, return to the task); 2b609ef T-0830: record lane T-0830-t0830
- Check: 1 four references byte-identical to the MacBook source: pass
- Check: 2 `grep -q 'capability-contracts.md'` in SKILL.md: pass
- Check: 3 unittest and packaging: pass

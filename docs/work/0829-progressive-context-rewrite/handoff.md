---
id: T-0829
title: "Ship the progressive-context rewrite, keeping the old references reachable"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0828]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-31
claimed_by: nonoun-author 2026-10-31
branch: lane/T-0829-t0829
worktree: ../sdlc-lite.worktrees/T-0829-t0829
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---
## Goal
`plugins/context/skills/progressive-context/` is the MacBook rewrite (context-system design: traversal, tier model, review rubric, semantic handoff, evaluation, scripts and tests), and the six references the rewrite drops stay reachable, so every live link into the skill still resolves.

## Context
- The user chose on 2026-10-31: replace the skill with the rewrite and keep the old references reachable.
- Source, read-only over SMB: `/Volumes/kimba/.codex/skills/progressive-context/` (2026-10-31 10:18; 30 files: SKILL.md, README, references, examples, schemas, scripts `validate.py` and `replay.py`, tests, templates).
- The rewrite drops `references/sdlc.md`, `evidence.md`, `a2ui.md`, `browser-harness.md`, `workflow-stages.md`, `performance-contract.json`; live docs link some of them (`git grep -n "progressive-context/references/" -- docs ':!docs/reports' ':!docs/work/.*'`).
- The repository guidance says the Context plugin owns durable intent, capability contracts, evidence and qualification for reuse (root `AGENTS.md`, `plugins/context/AGENTS.md`).
- It depends on T-0828 (knowledge-modeling), which the rewrite routes meaning questions to.

## Do
1. Replace the skill's files with the rewrite, leaving out `.DS_Store` and `__pycache__`. Never write to `/Volumes/kimba`.
2. Keep the six dropped references in `references/`, unchanged, and link them from the rewrite's SKILL.md in one short line or table row (capability contracts, evidence and reuse, SDLC links, A2UI and browser representations, workflow stages) so they remain discoverable.
3. Keep the packaging lines the plugin needs (Codex adapter line, entry skill name `progressive-context`).
4. Update `plugins/context/AGENTS.md` and the root `AGENTS.md` ownership line only as far as the rewrite changes what the skill does; add a context CHANGELOG `[Unreleased]` entry.
5. Run the rewrite's own tests and validator.

## Acceptance criteria
- The rewrite's tests pass: `python3 -m unittest discover -s plugins/context/skills/progressive-context/tests` exits 0.
- `for f in sdlc.md evidence.md a2ui.md browser-harness.md workflow-stages.md performance-contract.json; do test -f plugins/context/skills/progressive-context/references/$f || exit 1; done`
- `python3 scripts/check-packaging.py` exits 0 and `python3 plugins/sdlc/scripts/docs_check.py --root .` reports 0 errors.
- `git diff --check` is clean.

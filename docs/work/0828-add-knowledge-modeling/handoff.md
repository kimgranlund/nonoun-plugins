---
id: T-0828
title: "Add the knowledge-modeling skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-31
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---
## Goal
The context plugin ships `knowledge-modeling` as a skill, copied from the MacBook working copy, packaged like the other context skills for Claude Code and Codex.

## Context
- The user asked on 2026-10-31. Source, read-only over SMB: `/Volumes/kimba/.codex/skills/knowledge-modeling/` (2026-10-31 10:48; SKILL.md, `agents/openai.yaml`, 9 references, 3 examples, 4 templates).
- Packaging rules: `docs/specs/doc-standards/plugins.md`; check: `scripts/check-packaging.py` (skill size limit, Codex adapter line, routes). Plugin guidance: `plugins/context/AGENTS.md`.
- The progressive-context rewrite (T-0829) hands domain-meaning questions to `knowledge-modeling`.

## Do
1. Copy the skill into `plugins/context/skills/knowledge-modeling/`, leaving out `.DS_Store` and `__pycache__`. Never write to `/Volumes/kimba`.
2. Add whatever the packaging rules require of a context skill (the Codex adapter line, any route or listing in `plugins/context/AGENTS.md` or the plugin README, the context CHANGELOG `[Unreleased]` entry).
3. Keep the skill's text as authored except for packaging lines and broken relative links.

## Acceptance criteria
- `test -f plugins/context/skills/knowledge-modeling/SKILL.md`
- `python3 scripts/check-packaging.py` exits 0.
- `! find plugins/context/skills/knowledge-modeling -name .DS_Store -o -name __pycache__ | grep -q .`
- `git diff --check` is clean.

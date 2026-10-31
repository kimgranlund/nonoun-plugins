---
id: T-0828
title: "Add the knowledge-modeling skill to the context plugin"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-31
claimed_by: nonoun-author 2026-10-31
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

## Outcome

2026-10-31 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: b4c8b81a0985
- Changed: see commits
- Commits: 4a69332 T-0828: Add the knowledge-modeling skill to the context plugin; c2a3b46 T-0828: record lane T-0828-t0828
- Check: 1 `test -f plugins/context/skills/knowledge-modeling/SKILL.md`: pass
- Check: 2 `python3 scripts/check-packaging.py` exits 0: pass
- Check: 3 no `.DS_Store` or `__pycache__` under the skill: pass
- Check: 4 `git diff --check` is clean: pass
- Check: 5 Do 3 (text as authored): pass
- Check: 6 Do 2 (packaging lines): pass

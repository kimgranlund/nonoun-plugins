---
id: T-0826
title: "Import MacBook mathematical-design-system changes into the design plugin"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: nonoun-author 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plugins/design/skills/mathematical-design-system/` carries the general improvements made to the skill on the MacBook since the repo copy (2026-10-25), and nothing project-specific.

## Context
- The user asked (2026-10-30) to bring MacBook skill updates back into the repo, one ticket per skill.
- Source, read-only over SMB: /Volumes/kimba/.codex/skills/mathematical-design-system (2026-10-28 15:00).
- Differences found by a file-level diff: `SKILL.md` and `references/consumer-integration.md` changed; new `references/current-system.md`; Maison-specific additions `assets/maison-geometry/`, `scripts/check-maison-reference.mjs`, and a nested `.git` and `.openai` under `assets/proportion-lab/`.
- The repo copy is the shipped source; the MacBook copy was edited in place, so some changes may be general improvements and some may be Maison or machine specific.

## Do
1. Diff the source against `plugins/design/skills/mathematical-design-system/` file by file.
2. Take every change that is general to the skill. Leave out anything specific to one project (Maison, a single repo, machine paths), any nested `.git`, `.openai` or `.DS_Store`, and anything that would break the skill's Codex adapter line or the packaging rules in `docs/specs/doc-standards/plugins.md`.
3. In the report, list each file taken, each file left out and why.
4. Never write to `/Volumes/kimba`.

## Acceptance criteria
- `python3 scripts/check-packaging.py` exits 0.
- `! find plugins/design/skills/mathematical-design-system -name .git -o -name .DS_Store | grep -q .`
- `git diff --check` is clean.

## Outcome

2026-10-30 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 6a73d9df936a
- Changed: see commits
- Commits: 0663f2e T-0826: Import MacBook mathematical-design-system changes into the design plugin; 1063ccc T-0826: record lane T-0826-t0826
- Check: 1 `python3 scripts/check-packaging.py` exits 0: pass
- Check: 2 no `.git` or `.DS_Store` under the skill: pass
- Check: 3 `git diff --check` clean: pass
- Follow-up: note: references/current-system.md and the Maison geometry capture were... -> notes.md

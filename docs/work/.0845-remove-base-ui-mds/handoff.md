---
id: T-0845
title: "Remove base-ui and mathematical-design-system from design"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0842, T-0843, T-0844]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
branch: lane/T-0845-t0845
worktree: ../sdlc-lite.worktrees/T-0845-t0845
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The design plugin no longer ships `base-ui` or `mathematical-design-system`, and no record still points at them.

## Intent
- Do: delete both skill folders and repair every live reference.
- Non-goals: rewriting dated reports or closed tickets; changes to skill behaviour.
- Done when: the criteria below hold.

## Context
- Folders: `plugins/design/skills/base-ui/` and `plugins/design/skills/mathematical-design-system/`.
- Live references: `plugins/design/AGENTS.md` (skill table, Rules, Checks), root `README.md`, design and root `CHANGELOG.md` (add a Removed line under `[Unreleased]`, keep history), `scripts/check-packaging.py` if it names them, and any design skill text left after T-0842 to T-0844. Find them with `git grep -nE "base-ui|mathematical-design-system"` excluding `docs/reports/`, closed `.NNNN-*` tickets and CHANGELOG history.

## Do
1. `git rm -r` both folders.
2. Repair each live reference found by the grep.
3. Add the CHANGELOG `[Unreleased]` Removed lines.

## Acceptance criteria
- `test ! -e plugins/design/skills/base-ui -a ! -e plugins/design/skills/mathematical-design-system` exits 0.
- `git grep -nE "base-ui|mathematical-design-system" -- plugins/design README.md .claude-plugin .agents ':!*CHANGELOG.md' ':!plugins/design/skills/ui-kit-inspector/examples/maison-jig' ':!plugins/design/skills/wireframe-review/scripts/check-catalog-boundary.mjs'` prints nothing (replan: records and other plugins are T-0847), and `plugins/context/AGENTS.md` no longer uses `design:base-ui` as its naming example.
- `node scripts/check-build.mjs` in `component-variants`, `npm test` in the inspector-panel example and `node --test` in `ui-geometry` all exit 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Touch only reference lines; no behaviour change.

## Outcome

## Outcome

2026-11-12 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: ea5729f6c605
- Changed: see commits
- Commits: 2fc7c0a T-0845: remove base-ui and mathematical-design-system from design
- Check: 1 both skill folders removed: pass
- Check: 2 scoped grep prints nothing and context AGENTS.md no longer uses `design:base-ui`: pass
- Check: 3 component-variants, inspector-panel and ui-geometry checks: pass
- Check: 4 packaging and diff check: pass
- Follow-up: note: .sdlc/runtime/tasks/0845-remove-base-ui-mds/0845-solo-L2.md reports... -> notes.md

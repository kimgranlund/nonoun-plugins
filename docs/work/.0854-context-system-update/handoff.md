---
id: T-0854
title: "Update context-system from the MacBook copy"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-15
claimed_by: nonoun-author 2026-11-15
branch: lane/T-0854-t0854
worktree: ../sdlc-lite.worktrees/T-0854-t0854
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`context-system` in the context plugin matches the user's current MacBook copy, and everything here that leans on it still works.

## Intent
- Do: replace the repo copy with the source, then repair the three dependent skills and every live link into files the source moved or dropped.
- Non-goals: behaviour changes in dependents beyond following the new file names and formats; dated reports, closed tickets, CHANGELOG history.
- Done when: the criteria below hold.

## Context
- Source: `/Volumes/kimba/.claude/skills/context-system/` (110 files, no git). Target: `plugins/context/skills/context-system/`. Sync with `rsync -a --delete --exclude .DS_Store --exclude __pycache__ <source>/ <target>/`. `/Volumes/kimba` is read-only: never write under it.
- The source already holds the two features this repo carried in under T-0851 (`excludes-neighbor` in `scripts/validate_kos.py`, the decision-question doc type), so the repo copy needs no local additions. Confirm with a grep after the sync.
- What changed in the source: fixtures and templates moved from YAML to JSON (`vocabulary.json`, `rules.json`, `decision-question.rules.json`, `decision-question.vocabulary.json`; a `fixtures/yaml/` folder and `scripts/datafile.py` remain), the registry became a profile (`profile.json`, `schemas/profile.schema.json`, `templates/profile.md`), new scripts (`check.py`, `check_links.py`, `check_move.py`, `package.py`, `refresh_profile.py`), and `references/routing/` lost `a2ui.md`, `browser-harness.md`, `capability-contracts.md`, `evidence.md`, `sdlc.md`, `workflow-stages.md` and `performance-contract.json` (look under `references/routing/earlier/` and `references/routing/hosts/` for where they went).
- Dependents in `plugins/context/skills/`: `decision-questions`, `evaluation-system`, `classify-and-resolve`. Their scripts, tests, templates and references resolve `context-system/scripts/validate_kos.py` and `lint_cnl.py` by path and name `vocabulary.yaml`, `rules.yaml` and `templates/decision-question.rules.yaml`. Read `datafile.py` to learn which formats the validators accept now, then make the smallest repair so each dependent's tests pass and its text names files that exist.
- Live links into moved files: find with `git grep -n "context-system/references/routing" -- ':!docs/reports' ':!docs/work' ':!*CHANGELOG.md'` plus `python3 scripts/check-packaging.py` and `python3 plugins/sdlc/scripts/docs_check.py`; repoint each to the file's new home. Check `plugins/context/AGENTS.md` (the `## context-system` section and source row: date it 2026-11-15 and drop the "carried over" note), `plugins/context/HARNESS-NOTES.md` and `scripts/check-packaging.py`.
- Add a `### Changed` line under `## [Unreleased]` in `plugins/context/CHANGELOG.md`.
- If packaging flags a synced file (SKILL.md must be under 18000 characters), do not trim it: report blocked with the output.

## Do
1. Sync the skill and run its own tests.
2. Repair the three dependents.
3. Repoint live links, update the guidance and changelog, run the checks.

## Acceptance criteria
- `diff -rq --exclude .DS_Store --exclude __pycache__ /Volumes/kimba/.claude/skills/context-system plugins/context/skills/context-system` prints nothing.
- `python3 -B -m unittest discover -s tests` exits 0 in each of `context-system`, `decision-questions`, `evaluation-system`, `classify-and-resolve` and `context-fog-of-war`, with no test skipped in `classify-and-resolve` or `decision-questions`.
- `python3 scripts/check-packaging.py` exits 0, `python3 plugins/sdlc/scripts/docs_check.py` reports 0 errors, and `git diff --check` is clean.
- No live file links to a path that no longer exists under `plugins/context/skills/context-system/` (packaging and docs_check cover this; name any link you repointed in the report).

## Constraints
- Never write under `/Volumes/kimba`.
- Do not hand-edit the synced skill.

## Outcome

2026-11-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 992037cfca8c
- Changed: see commits
- Commits: ad2882c T-0854: update context-system from the MacBook copy
- Check: 1 diff -rq of the source against the target prints nothing: pass
- Check: 2 unittest discover exits 0 in the five skills, no skips in classify-and-resolve or decision-questions: pass
- Check: 3 check-packaging exits 0, docs_check 0 errors, git diff --check clean: pass
- Check: 4 no live link to a missing path under plugins/context/skills/context-system/: pass
- Follow-up: note: plugins/context/skills/classify-and-resolve/references/growth.md:78... -> notes.md

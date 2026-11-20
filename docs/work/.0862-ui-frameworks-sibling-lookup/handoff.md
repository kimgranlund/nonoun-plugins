---
id: T-0862
title: "ui-frameworks finds sibling skills inside the plugin"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-frameworks` scripts find `ui-geometry`, `ui-colors` and its other sibling skills when the design plugin is installed without copies in `~/.claude/skills`.

## Intent
- Do: make the sibling lookup try the plugin's own `skills/` folder first.
- Non-goals: any other change to `ui-frameworks`; changing what the scripts generate.
- Done when: the criteria below hold.

## Context
- `plugins/design/skills/ui-frameworks/scripts/tokens.mjs` and `icons.mjs` (and any other script there that does the same; grep for `SKILLS_DIR` and `.claude/skills`) read sibling skills from `SKILLS_DIR` or `~/.claude/skills`. In a plugin install the siblings sit beside the skill at `../<name>` relative to the skill folder.
- Fix: resolution order `SKILLS_DIR` when set, then the skill's own parent folder (resolved from `import.meta.url`), then `~/.claude/skills`; the error message when none has the sibling names all the places tried. Put the resolver in one helper the scripts share.
- This skill is synced from the user's MacBook copy, so this is a deliberate local difference: say so in the `ui-frameworks` row of `plugins/design/AGENTS.md` ("differs from source: sibling lookup, T-0862") so the next sync keeps it, add a `### Fixed` line under `## [Unreleased]` in `plugins/design/CHANGELOG.md`, and note in your report that the user should take the same change upstream.
- Read `plugins/design/AGENTS.md` first.

## Do
1. Add the shared resolver and use it.
2. Prove it with `HOME` pointed at an empty folder.
3. Record the difference.

## Acceptance criteria
- With `HOME` set to an empty scratch folder and `SKILLS_DIR` unset, the scripts that read siblings run to success from the plugin tree (name each command and its exit code in the report); before the change the same command fails (observed red, stated in the report).
- With `SKILLS_DIR` pointing at a folder that lacks the sibling, the error names every place tried.
- `node scripts/manifests.mjs --check` and `node scripts/lint-recipes.mjs` exit 0 in `ui-frameworks`; `python3 scripts/check-packaging.py` exits 0; `git diff --check -- . ':!plugins/design/skills/ui-frameworks/docs' ':!plugins/design/skills/ui-frameworks/kit'` is clean.

## Constraints
- Generated output is byte-identical to before for the same inputs.
- Never write under `/Volumes/kimba`.

## Outcome

2026-11-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 0a82cf148510
- Changed: see commits
- Commits: 20f170a T-0862: ui-frameworks finds sibling skills inside the plugin
- Check: 1 Scripts that read siblings succeed with empty HOME and SKILLS_DIR unset, and failed before: pass
- Check: 2 With SKILLS_DIR at a folder lacking the sibling, the error names every place tried: pass
- Check: 3 manifests, lint-recipes, check-packaging, diff --check: pass
- Follow-up: note: with SKILLS_DIR set but lacking a file, the resolver falls through... -> notes.md
- Follow-up: note: the user should take the same change upstream to the MacBook source... -> notes.md

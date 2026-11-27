---
id: T-0891
title: "Skill descriptions break claude.ai limits: angle brackets and over 1024 chars"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-27
claimed_by: nonoun-author 2026-11-27
branch: lane/T-0891-t0891
worktree: ../sdlc-lite.worktrees/T-0891-t0891
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every skill `description` in the four plugins is at most 1024 characters and contains no `<...>` tag, and `scripts/check-packaging.py` fails on either defect, so the claude.ai marketplace sync shows no warnings.

## Repro
1. Sync the `nonoun-plugins` marketplace on claude.ai at commit `f750120` (v1.0.14).
2. Open the marketplace's "1 notice, 12 warnings" panel.

## Expected
No warnings. Claude Code and claude.ai read the same description.

## Actual
Quoted from the claude.ai panel, 2026-11-27 10:34:
- sdlc: "Skill 'skills/build': SKILL.md description cannot contain XML tags", "claude.ai stores its description with angle brackets removed. Claude Code reads the full text from the file." The same pair for `skills/handoff-format`, `skills/handoff` and `skills/run-plan`.
- context: "Skill 'skills/classify-and-resolve': field 'description' in SKILL.md must be at most 1024 characters", "claude.ai stores its description cut to 1024 characters."
- design: the same length pair for `skills/explore-variants`.

Measured locally: `build` has `<step handoff.md>`, `handoff-format` and `handoff` have `<work root>/<task>`, `run-plan` has `<plan-doc.md>`; `classify-and-resolve` is about 1067 characters (folded `>` scalar), `explore-variants` 1218.

## Context
- The design notice ("Executable files or settings may differ") is expected after a release and is out of scope.
- `scripts/check-packaging.py` checks manifests and skill sizes but not description length or angle brackets.
- `explore-variants` is synced from the MacBook copy; record the shortened description under "differs from source" in `plugins/design/AGENTS.md`. `classify-and-resolve` is authored here.
- Rewrite placeholders in words or another notation (for example `[step handoff]`, `WORK_ROOT/TASK`) and keep each description's trigger meaning. Shorten the long ones by cutting detail the SKILL.md body already holds.
- Codex generated files: if a description is mirrored elsewhere (agents TOML, catalogs), regenerate rather than hand-edit (`codex_roles.py generate --check`).

## Constraints
- The new gate lands with the fix: positive case on the fixed tree, and an observed negative control (a temp copy with an angle bracket or a 1025-character description makes `check-packaging.py` exit non-zero).
- Count the description after YAML parsing (folded and literal scalars), as the host does.
- Do not edit any CHANGELOG.

## Acceptance criteria
- `python3 scripts/check-packaging.py` exits 0 on the fixed tree.
- The negative control exits non-zero and names the skill and the limit.
- No `SKILL.md` description under `plugins/` contains `<` followed by `>`, and none exceeds 1024 characters after YAML parsing.
- `git diff --check` is clean.

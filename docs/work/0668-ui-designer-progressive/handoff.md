---
id: T-0668
title: "ui-designer reads SKILL.md first and opens references by cue"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
In review and plan modes the ui-designer reads each routed repo SKILL.md first and opens a reference only when that SKILL.md's cue matches the change, instead of loading every reference.

## Intent
- Do: (1) `plugins/sdlc-lite/agents/ui-designer.md` `## Method`: add one sentence after "Find the design system first": "Read each repo skill that AGENTS.md routes to the files in scope; read its SKILL.md first and open a reference only when its cue in SKILL.md matches the diff or the plan." (2) Pin the phrase `open a reference only when its cue` in `UI_DESIGNER_PHRASES` (`plugins/sdlc-lite/scripts/check.py:761`). (3) Regenerate `agents/ui-designer-L1.md` with `claude_roles.py generate` and the Codex agents with `codex_roles.py generate`.
- Non-goals: routing skills into handoffs or prepare (T-0647, T-0648). Generate mode wording beyond the shared Method sentence. No model or effort change.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #28, ui-kit-neue audit 2026-10-20.
- In ui-kit-neue, 3 of 6 non-author agents that opened `.agents/skills/geometry-authoring/references` loaded all four references in one `cat` (one returned about 21 KB); two reviewers probed a nonexistent `recipe-authoring/references`.
- Confirmed in this repo: `plugins/sdlc-lite/agents/ui-designer.md` never mentions repo skills; `## Method` starts at `ui-designer.md:21` with "Find the design system first" at `:22`. The phrase pin tuple is `plugins/sdlc-lite/scripts/check.py:761`, read by `ui_designer_bad` at `check.py:762-763`.
- `agents/ui-designer-L1.md` is generated (`plugins/sdlc-lite/AGENTS.md:19`); edit only `ui-designer.md`.
- T-0649 also edits `ui-designer.md` (Output section); run the two in different waves.

## Constraints
No other change to the ui-designer contract. No model or effort change.

## Acceptance criteria
1. `grep -c 'open a reference only when its cue' plugins/sdlc-lite/agents/ui-designer.md plugins/sdlc-lite/agents/ui-designer-L1.md` prints 1 for each file.
2. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0, and with the sentence removed from `ui-designer.md` it reports `agents/ui-designer.md missing "open a reference only when its cue"` (the case fails with the change reverted).
3. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0 and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
4. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.

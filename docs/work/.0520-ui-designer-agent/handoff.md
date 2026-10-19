---
id: T-0520
title: "Add a ui-designer role: plans, reviews and generates semantic DOM and CSS, inside-out and outside-in, design-system aware"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0519]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A new pipeline role, `ui-designer`, that plans, reviews and generates correct, semantic DOM structure and excellent CSS, aware of the design system and sibling styling around the code it touches.

## Intent
- Do: add the role end to end, as the existing roles are wired. A role file `plugins/sdlc-lite/agents/ui-designer.md` (the contract: brief, work, output sections, result schema in `scripts/results.py`), `adapters/claude/levels.json` rows, `adapters/codex/models.json` rows, `run.sh` case rows, `skills/level-rubric/SKILL.md`, generated `ui-designer-L1|L2` Claude agents and Codex TOMLs, a `dispatch.py` and `check.py` agreement, and one eval record that locks the table (read `.sdlc/evals/AGENTS.md`).
- Do: levels. Claude L1 = opus medium, L2 = opus high. Codex L1 = gpt-6.1-sol medium, L2 = gpt-6.1-sol high. These are the user's stated choices (2026-10-13).
- Do: three modes named in the brief: plan (a DOM and CSS structure with reasons, before any build), review (judge existing DOM and CSS, findings tied to file:line, never rewrites), generate (write the markup and CSS in the tree). Mode comes from the handoff. Generate is the only mode that edits.
- Do: the role's method, written into the role body as two passes. Inside out: the element's own semantics (right element for the content, landmark and heading structure, accessible name and role, states, content-driven sizing, logical properties, the smallest selector that works). Outside in: the context it lives in (design tokens and theme variables, the system's component and utility patterns, sibling and collection styling such as lists, cards, grids and form groups, cascade layers and specificity budget, responsive container behavior). Find the global or contextual design system first (tokens file, theme, component library, existing CSS conventions) and follow it; a deviation is stated with a reason.
- Do: output sections defined by the role contract with a findings or decisions list, a `Context used` section (which design-system and peer files it read), and a `Carry forward` section like the other roles.
- Do: a live check on a throwaway project: one plan, one review, one generate run each producing a valid result file.
- Non-goals: framework-specific code generation, visual regression tooling, changes to the builder or verifier contracts, new skills beyond what the role needs.
- Done when: `check.py`, both `generate --check` runs, `dispatch.py selftest`, `codex-selftest.py`, `results.py` selftest and `evals.py check` pass; a negative control shows the result schema rejects a missing key section; the throwaway live run produced three valid result files.

## Context
- Model for each choice is fixed by the user, do not re-tune: Claude `opus` at `medium` and `high`; Codex `gpt-6.1-sol` at `medium` and `high`. A table change needs a new eval in `.sdlc/evals/` and `evals.py lock` (T-0518 allows a same-date higher-numbered eval).
- Follow the closest existing read-mostly role for wiring: `architect` (design, writes only under the artifacts dir) for plan and review modes, `builder` for generate mode's edit rights. Decide whether `ui-designer` is one role with a mode or needs the builder's write hook allowances; record the choice in the plan.
- Role agents are generated from role file plus `levels.json` (`claude_roles.py generate`); Codex TOMLs from `codex_roles.py generate`. Never edit a generated file.
- Authoritative sources: `plugins/sdlc-lite/AGENTS.md` (contracts, verification list), `scripts/results.py` (result schema), `skills/level-rubric/SKILL.md`, `docs/references/codex-role-execution.md`.
- Depends on T-0519 only because that ticket also edits `levels.json` and `models.json`; build after it merges to avoid a conflict.

## Constraints
Preserve every existing role's contract, level and model. Keep one authoritative location per fact. Run the shared-runner validation row of the root matrix (`bash plugins/sdlc-lite/scripts/check.sh` plus packaging checks) before closing, and add a release-note line for the next patch.

## Plan review
- plan defect: step 2: `dispatch.py prepare builder L2` refused the step handoff (`steps.py lint`): `cited path does not exist: .sdlc/plan/handoff.md`, `cited path does not exist: .sdlc/review/handoff.md`, `cited path does not exist: .sdlc/generate/handoff.md`; `plan defect: replan this step (/chain 3)`. These three are handoffs inside the throwaway project the step creates, not paths in this repo; lint reads any backticked `.sdlc/...` path in a step handoff as a repo path that must exist. Step 1 is built and verified (pass) and stays as is; rewrite step 2 only, naming the throwaway project's files so that no backticked path reads as a repo path (for example describe them in prose, or as paths under a `<project>` placeholder), and run `steps.py lint` on the result.

## Closed

2026-10-13: warnings acknowledged: verifier passed; unverified items (Codex host, sub-agent dispatch path, plan/review non-edit enforcement) go to T-0522 and the 0.22.7 release record

> - process deviation: red-checkpoint: retrospective: attempt ed8962fc81a54a4d916b5bc57485e74a, handoff sha256 1b1afbecdf9b, 5 of 5 (red) criteria without a pre-edit red control (step 2: the live-run results validate, the `## Mode` key per file, the status files, the report links, and the `## Release note` heading). `redck.py record` ran after step 1's 30 files were already uncommitted in the tree, so it stored the controls as retrospective. The builder says all five were red before step 2's own edits, and the verifier saw each one red against base by absence or by a mutated /tmp copy. Both steps passed, but the passing verdict does not clear this deviation.
> - Step 2 report figures are unverified. The throwaway project was gone when the verifier ran, so the retained `.txt` results could not be compared byte for byte with the run outputs. The per-run `runs.jsonl` behind the report's model, effort, and cost columns could not be read. No criterion names them. The report header's Claude Code version (`2.1.296`) was not re-run.
> - The live run is partial. The report's `## Not proven` section lists the Codex host, the sub-agent dispatch path with the generated `ui-designer-L<n>` definitions, whether plan and review modes stay out of the tree (nothing enforces it), and output quality. The generated markup and CSS were not opened in a browser.
> - The plan needed one replan. Step 2's first handoff was refused by `steps.py lint`, which read backticked throwaway-project paths as repo paths. Step 1 stayed as built and step 2 was rewritten.

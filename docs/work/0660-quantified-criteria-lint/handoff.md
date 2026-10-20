---
id: T-0660
title: "Plan lint flags universally quantified prose criteria with no command"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A universally quantified prose criterion ("lists every public prop") can no longer pass plan lint or the verifier without a mechanical check or a full enumeration.

## Intent
- Do: (1) `lint_steps` in `plugins/sdlc-lite/scripts/steps.py` adds a finding `steps: <plan> step <n>: plan defect: quantified prose criterion has no command: <line>` for a criterion line with no command span (`line_spans` plus `is_command`) whose prose holds the whole word `every`, `all` or `each`, unless the line names an enumeration or sample (`enumerate`, `N of N`, `sample`); the message asks for a runnable check or an enumeration instruction. (2) `skills/checking-rules/SKILL.md` adds a rule: a quantified prose criterion is answered with an enumeration, `k of N` with a source pointer per item, never a bare pass. (3) `steps.py selftest` cases for the flagged line, a quantified line with a command, and one naming an enumeration.
- Non-goals: ticket handoff criteria outside a step plan; `plan_check.py` plan-doc rules; rewriting existing closed criteria.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #20, ui-kit-neue audit 2026-10-20.
- Evidence: T-0084, T-0085 and T-0088 criteria such as "Each new meta.ts has ... every public React prop" were marked pass by reading; shipped manifests still lacked required props (Toaster `toaster`, IconButton `icon`).
- Home: `lint_steps` (`plugins/sdlc-lite/scripts/steps.py:2065`), run by `steps.py lint` and split. It inspects only command spans of each criterion line (`criteria_lines` `:701`, `line_spans` `:738`, `is_command` `:710`); a prose line is never checked today. `plan_check.py check_plan` (`plugins/sdlc-lite/scripts/plan_check.py:589`) covers plan docs, not step plans.
- `plugins/sdlc-lite/skills/checking-rules/SKILL.md` (79 lines) has no enumeration rule; verifiers load it through their generated `skills:` list, so no agent regeneration is needed.
- Note the word `each` also starts prose like "for each changed file" that `is_command` already treats as prose (`plugins/sdlc-lite/scripts/steps.py:715`); such a line with a command span is not flagged.

## Constraints
A criterion line with a command span is never flagged by this rule. Other lint findings are unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0. Its new cases: `- meta.ts lists every public prop` fails lint with `quantified prose criterion has no command`; ``- every prop is listed: `node check.mjs` `` passes; `- enumerate every public prop as k of N with a source line` passes. The first case fails with the change reverted.
2. `grep -n -i 'enumerat' plugins/sdlc-lite/skills/checking-rules/SKILL.md` prints the new rule.
3. `python3 scripts/check-packaging.py` exits 0.
4. `git diff --check` exits 0.

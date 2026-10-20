---
id: T-0649
title: "ui-designer review writes a verdict, blocking flags and rule provenance"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ui-designer review result opens with a verdict a verifier can read, marks each finding blocking or advisory, and names the rule each finding enforces or the guidance gap it exposes, so a "the review passes" criterion is checkable and recurring defects can be promoted into repo skills.

## Intent
- Do: (1) `plugins/sdlc-lite/agents/ui-designer.md` `## Output`: in review mode a `## Verdict` section directly after `## Mode` holds one of `pass`, `pass-with-notes`, `changes-required`; each `## Findings` line takes the form `- <file:line>: blocking|advisory: <what is wrong>: <what to do instead>. Rule: <skill>#<section>` or `Rule: gap (proposed: "<one line>")`; a `## Guidance gaps` section after `## Findings` lists every `Rule: gap` proposal once (`None` when there is none, and in plan and generate modes). Regenerate the level variants with `claude_roles.py generate` and the Codex agents with `codex_roles.py generate`. (2) `plugins/sdlc-lite/scripts/results.py`: the ui-designer schema gains the optional `Verdict` and `Guidance gaps` sections in that order; `validate` refuses a review-mode result with no `## Verdict` or a value outside the three, and refuses `pass` or `pass-with-notes` beside a finding marked `blocking`; selftest cases for each. (3) `plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md` `## Patterns` gains a "UI review criterion" row: ``grep -A1 '^## Verdict' <review result>`` prints `pass` or `pass-with-notes`, so a step or ticket criterion names the verdict field instead of "a review passes".
- Non-goals: aggregating `Rule: gap` items across tickets (T-0650). A re-review dispatch after the builder or solo applies blocking findings (the verdict criterion makes the need visible; the flow change is a separate ticket if still wanted). No change to plan or generate mode output beyond `None` sections. No model or effort change.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #12, ui-kit-neue audit 2026-10-20. This ticket is part a (verdict, blocking flags, rule provenance, validation, criterion shape); part b is T-0650.
- In ui-kit-neue, 4 of the 7 verifier fails in component tickets were the criterion "a ui-designer review of the recipe change passes", which a findings list cannot satisfy. None of 44 reviews had a verdict line; 9 of 386 findings cited a rule; forced-colors defects recurred in 15 tickets and RTL defects in 13 with no rule in any skill.
- Confirmed in this repo: the output contract is `plugins/sdlc-lite/agents/ui-designer.md:42-61` (sections Mode, Decisions, Findings, Changes, Context used, Carry forward); a finding is `- <file:line>: <what is wrong>: <what to do instead>` at `ui-designer.md:52`, with no verdict, severity or rule field. The review mode rule is `ui-designer.md:14`.
- Validation: `plugins/sdlc-lite/scripts/results.py:79-83` (ui-designer key `Mode`, sections tuple); only the key section is required, sections are order-checked. The verifier's "Verdict pass beside a non-pass criterion" refusal in `_criteria_error` (`results.py:274-295`) is the precedent for the blocking-finding refusal. Selftest fixture body for ui-designer at `results.py:402-403`.
- `agents/ui-designer-L1.md` is generated from `ui-designer.md` and `adapters/claude/levels.json` by `plugins/sdlc-lite/scripts/claude_roles.py` (`plugins/sdlc-lite/AGENTS.md:19`); never edit it by hand. `check.py` pins phrases of the role at `plugins/sdlc-lite/scripts/check.py:761` (`UI_DESIGNER_PHRASES`) and lists it as a Carry forward producer at `check.py:747`.
- No handoff template in this repo holds a ui-designer review criterion today (`grep -rn ui-designer plugins/sdlc-lite/skills/handoff-format` finds nothing), so the criterion shape is new. `skills/handoff-format/SKILL.md` is 29,854 characters and T-0659 trims skills under 18,000, so the row goes in `references/writing-rules.md`, not SKILL.md.

## Constraints
Existing plan and generate mode results keep validating unchanged. Existing ui-designer result files with no `## Verdict` in plan or generate mode stay valid. No model or effort change in `levels.json` or `models.json`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/results.py selftest` exits 0 with new cases: a review-mode result with `## Verdict` `changes-required` and one `blocking` finding validates; a review-mode result with no `## Verdict` is refused; `## Verdict` `maybe` is refused; `## Verdict` `pass` beside a `blocking` finding is refused; a plan-mode result with no `## Verdict` validates. The `pass` beside `blocking` case fails with the change reverted.
2. `grep -c 'Rule: gap (proposed:' plugins/sdlc-lite/agents/ui-designer.md plugins/sdlc-lite/agents/ui-designer-L1.md` prints a count of at least 1 for both files, and `grep -n '## Guidance gaps' plugins/sdlc-lite/agents/ui-designer.md` finds the section.
3. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0 and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
4. `grep -n 'UI review criterion' plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md` finds the row naming `## Verdict`.
5. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0.
6. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Outcome
Lane solo. ui-designer review results now open with `## Verdict` (pass, pass-with-notes, changes-required), mark each finding blocking or advisory with a `Rule:` provenance or `Rule: gap (proposed: ...)`, and list gaps under `## Guidance gaps`.
- `plugins/sdlc-lite/agents/ui-designer.md`: Verdict, finding form, Guidance gaps; review mode line names the verdict. Regenerated `agents/ui-designer-L1.md` and `adapters/codex/agents/sdlc-ui-designer-l1.toml`.
- `plugins/sdlc-lite/scripts/results.py`: schema gains Verdict and Guidance gaps; `_ui_review_error` refuses a review with no or an unknown Verdict, and pass or pass-with-notes beside a blocking finding; 7 selftest cases plus a stub negative control. With the rule removed, the pass-beside-blocking case misses (observed).
- `plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md`: "UI review criterion" pattern row.
- Checks: every acceptance criterion exit 0 (results selftest, greps, claude_roles and codex_roles `generate --check`, check.py, `git diff --check`, check-packaging).

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: no `red-checkpoint` process deviation line was printed by redck.py, and no `(red)` criteria exist in the handoff.) · verifier: verifier-L2 (sonnet) · base: 92b2df57cd83
- Changed: see commits
- Commits: 24452f0 T-0649: ui-designer review writes a verdict, blocking flags and rule provenance
- Check: 1 results.py selftest exits 0 with the new cases: pass
- Check: 2 Rule: gap count and Guidance gaps section: pass
- Check: 3 generate --check for both: pass
- Check: 4 UI review criterion row: pass
- Check: 5 check.py: pass
- Check: 6 diff --check and packaging: pass

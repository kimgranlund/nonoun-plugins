<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- There are no plan, builder, or verifier files in the artifacts dir, and no `step-*` folders. The only files are `handoff.md` and the filer's own log. No step ran through the loop, so there is no verifier verdict.
- Nothing shows that the three edits were made or that `check.sh` stayed green. The PR body and changelog below describe the handoff's stated scope, not confirmed results.
- The handoff's Intent section is empty (Do, Non-goals, Done when).

## PR title
T-0098: Drop history ids and dates from level-rubric, checks-that-bite, and file skill prompts

## PR body
### Summary
Applies the user-approved prompt audit of 2026-09-25. Shipped skill prompts should carry no ticket ids or dates that the loading model can't use. The decision record for the user decision stays in CLAUDE.md.

### Changes
Per the handoff, three wording edits:
1. `skills/level-rubric/SKILL.md`: drop `(user decision, T-0005)`.
2. `skills/checks-that-bite/SKILL.md`:
   - "Two measured NCs that went green instead, both from 2026-07-29:" becomes "Two that went green instead:".
   - "Each entry measured in the wild, each a check that passed while examining nothing." becomes "Each entry is a check that passed while examining nothing."
3. `skills/file/SKILL.md` step 3.2: the example "(T-0047): ... duplicate of T-0002 `div crashes on zero divisor`" becomes "For example, a follow-up ... is a likely duplicate of an open ticket titled `div crashes on zero divisor`".

The handoff says to apply this after batch 17 merges, to avoid conflicts.

### Verification
Not verified from the artifacts. There are no builder or verifier results. The handoff requires `scripts/check.sh` to stay green. Run it before merging.

## Changelog entry
- Skill prompts (`level-rubric`, `checks-that-bite`, `file`) no longer carry ticket ids or dates. Wording only, with no behavior change intended.

## Follow-ups
None

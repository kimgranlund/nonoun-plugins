<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0098: Drop history ids and dates from level-rubric, checks-that-bite, and file skill prompts

## PR body
### Summary
Shipped skill prompts should carry no ticket ids or dates that the loading model can't use. This applies the three hunks of the 2026-09-25 prompt audit, which the user approved. `CLAUDE.md` is not edited, so the T-0005 decision record stays there.

### Changes
The conductor made these wording swaps as a trivial edit, with no builder run. Only three files under `plugins/sdlc-lite/skills/` changed.
1. `level-rubric/SKILL.md`: dropped `(user decision, T-0005)`.
2. `checks-that-bite/SKILL.md`:
   - "Two measured NCs that went green instead, both from 2026-07-29:" is now "Two that went green instead:".
   - "Each entry measured in the wild, each a check that passed while examining nothing." is now "Each entry is a check that passed while examining nothing."
3. `file/SKILL.md` step 3.2: the example now reads "For example, a follow-up ... is a likely duplicate of an open ticket titled `div crashes on zero divisor`". It no longer names T-0047 or T-0002.

### Verification
A verifier L1 run (sonnet, medium) in step-1 returned **pass**:
- The old phrases (`T-0005`, `2026-07-29`, `measured in the wild`, `Two measured`, `T-0047`, `T-0002`) are gone from the three files, and the new wording is present. The verifier noted each negated check is red at HEAD.
- `git diff --name-only -- plugins` lists only the three skill files, and the full diff shows only the named lines changed. The generic `T-NNNN` placeholders in `file/SKILL.md` are untouched.
- `git diff --quiet HEAD -- CLAUDE.md` exits 0.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. Its tail shows the run selftest, hook selftest, hook live probe selftest, shellcheck, and plugin validate all passing.

The handoff says to apply this after batch 17 merges, to avoid conflicts.

## Changelog entry
- Skill prompts (`level-rubric`, `checks-that-bite`, `file`) no longer carry ticket ids or dates. This is wording only, with no behavior change.

## Follow-ups
None

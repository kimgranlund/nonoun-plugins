<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0084: Port checking-rules into sdlc-lite and load it in the verifier

## PR body
### Summary
Adds a trimmed `checking-rules` skill to sdlc-lite and loads it into the verifier next to `checks-that-bite`. The verifier gets three rules for reviewing work:
- Evidentiary symmetry: dismissing a concern needs as much evidence as filing one.
- Runtime over claim: run the check instead of trusting what the builder says.
- Steelman before filing: make the strongest case against each fail reason before filing it.

The shipped plugin now carries this skill itself, so it does not depend on harness, which the user keeps disabled.

### Changes
- `plugins/sdlc-lite/skills/checking-rules/SKILL.md` (new): a trimmed port of harness checking-rules 3.19.6, reworded for a verifier checking a builder's step against its acceptance criteria. It keeps the Procedure, Output contract, Failure branches, and Example sections. It drops "The invariant's unit", "Semantic-diff soft size budget", and every reference to harness skills or flows. It says it complements `checks-that-bite`.
- `plugins/sdlc-lite/agents/verifier.md`: adds `checking-rules` under `skills:`, plus one sentence in the "A criterion with no evidence fails." paragraph. The sentence says that a dismissal or an accepted builder claim must cite the check behind it, and that each fail reason is steelmanned before it is filed. The verdict format is unchanged.
- `CLAUDE.md`: the Agent skills line now lists both verifier skills. `.claude/agents/sdlc-lite-author.md` has no line listing the verifier's skills, so it is unchanged.
- `plugins/sdlc-lite/.claude-plugin/plugin.json`: version 0.8.3 to 0.8.4.

### Verification
There was one step, built at L2 and verified at L1. The verdict was pass on all 14 criteria.
- `SDLC_DRY_RUN=1 scripts/run.sh verifier L1 <handoff>`: the appended system prompt file contains both `# Skill: checks-that-bite` and `# Skill: checking-rules`.
- The new SKILL.md was grepped for:
  - no harness terms, no em dashes, and no bold inline labels;
  - the three rule names and three section headings present;
  - the dropped sections absent.
- The verifier also read the whole file and confirmed it reads as a verifier's discipline with no harness context left.
- `verifier.md` still has exactly its four output headings.
- `run.sh`, `level-rubric`, `checks-that-bite`, and `sdlc-lite-author.md` are unchanged (`git diff --quiet HEAD`).
- `scripts/check.sh` exited 0 on a fresh run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- 0.8.4: The verifier now loads a `checking-rules` skill (ported from harness and trimmed). A dismissal or an accepted builder claim must cite a check, and each fail reason is steelmanned before it is filed.

## Follow-ups
None

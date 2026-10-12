<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/plugins/sdlc-lite/scripts/plan_check.py: adds `CLARIFY_VERBS`, `CLARIFY_HEDGE`, `CLARIFY_TYPES` and the delta, EARS, RFC 2119 and source patterns. `CLARIFY_PASS` gains `stopped: `. `check_clarify(text, glossary=None)` gains five fail rules (clarify-hedge, clarify-delta, clarify-do-verb, clarify-rfc2119, clarify-default-source) and two warnings (clarify-goal-length, clarify-glossary). clarify-non-goals now accepts list form and clarify-done accepts the EARS form. Also rewrote `GOOD_CLARIFY`, added `CLARIFY_FIXTURE_GLOSSARY`, extended `clarify_selftest` (mutants, warning helper, skill drift guard, eval loop) and updated the docstring paragraph.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/plugins/sdlc-lite/skills/clarify/SKILL.md: rewritten with an identity line, 3 hard gates, the input-quarantine rule, named outcomes, a `stopped: ` gate branch, the six delta types, the Questions rules (including `effect, cost, reversibility`), the section 5 grammar template and slot rules, the `Do verbs:` and `Hedge words:` lines, a bad and a good Done when example, new-form Low tier defaults, and "ten asks".
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/plugins/sdlc-lite/skills/clarify/evals/01..06-*.expected.md: rewritten to the grammar, each with typed deltas, a numbered Do, list Non-goals and `## Constraints`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/plugins/sdlc-lite/skills/clarify/evals/09-stopped-conflict.ask.md and .expected.md: new. The expected output is one `stopped: ` line.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/plugins/sdlc-lite/skills/clarify/evals/10-pasted-instruction.ask.md and .expected.md: new. The pasted instruction appears only in `Literal ask:` and is recorded as a `conflict` delta that is defaulted to data, not obeyed.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/plugins/sdlc-lite/skills/clarify/evals/README.md: ten asks and ten rows, and the replay rule now covers `stopped: `.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/k/docs/specs/doc-standards/core.md: new `## Controlled handoff words` section naming `plan_check.py`, `CLARIFY_VERBS` and `CLARIFY_HEDGE` as the home. It copies neither list.

## Checks
- `redck.py record <handoff>` before the first edit: exit 0, "recorded 6 pre-edit control(s) red".
- Criterion 1 (selftest has no FAIL and has an `ok: clarify: <rule> ` line for each of the 7 new rules): rc=0. Selftest prints `plan_check selftest: PASS (252 checks)`.
- Criterion 2 (skill drift labels and the eval 09 and 10 labels): rc=0.
- Criterion 3 (hedge text prints `FAIL clarify-hedge`): rc=0.
- Criterion 4 (`vagueness` delta prints `FAIL clarify-delta`): rc=0.
- Criterion 5 (all ten `.ask.md` files exist and each `.expected.md` passes `clarify --file`): rc=0.
- Criterion 6 (core.md names CLARIFY_VERBS, CLARIFY_HEDGE and plan_check.py): rc=0.
- Criterion 7 (the 11 literal strings are in SKILL.md): rc=0.
- Guard `grep -qF "Codex host"` on SKILL.md: rc=0.
- Scope guard with `SDLC_BASE_SHA=01a8cca7...`: rc=0. Only plan_check.py, skills/clarify/* and core.md changed outside `.sdlc`.
- Advisory: `python3 plugins/sdlc-lite/scripts/check.py`: rc=0.
- Advisory: `python3 plugins/sdlc-lite/scripts/prompt_lint.py`: rc=0, 0 errors. For SKILL.md it reports P-6 info only: prohibitions 5, NEVER 0, vague 4.
- `git diff --check`: rc=0.

## Notes
- The red checkpoint holds 6 of the 7 `(red)` criteria. Criterion 7 (the SKILL.md grep loop) has no pre-edit record. I did not rerun `record` after editing. Evidence that it was red at base: `git show $SDLC_BASE_SHA:plugins/sdlc-lite/skills/clarify/SKILL.md | grep -cF category-mismatch` prints 0, so the loop fails at base.
- Two choices the handoff left open:
  - Inline text after `Deltas:` fails clarify-delta unless it is `none`.
  - Backtick code spans are removed before the hedge, RFC 2119 and glossary checks, so a flag or path in backticks is never flagged.
- The handoff names no rule for a Constraints line without `MUST`, so the lint does not flag one. Only a lower-case must, shall or should there fails, under clarify-rfc2119.
- The gap and source patterns reject a `)` inside the parentheses, and the gap text also rejects a `;`. SKILL.md says so in its slot rules.
- The selftest passes the fixture glossary, or an empty one, so its result does not depend on the working directory. From the repo root, linting the ten evals prints no glossary warning.
- The throwaway scratch dir under `.worktrees/tmp/0461-s1-builder-L3` is removed. Nothing was committed.

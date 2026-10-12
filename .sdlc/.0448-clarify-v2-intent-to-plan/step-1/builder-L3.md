<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/scripts/plan_check.py: adds the `clarify` kind, with `check_clarify(text)` and helpers implementing the six rules. Also adds it to the `run_check` dict and the argparse `choices`, adds `GOOD_CLARIFY` and `clarify_selftest`, makes `expect()` print `clarify: ` labels, and updates the module docstring usage and first line.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/README.md: new. Lists the cases and the replay steps.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/0{1..8}-*.ask.md: 8 new files, one per case.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/evals/0{1..8}-*.expected.md: 8 new files, one per case.

## Checks
- `python3 .../redck.py record .sdlc/0448-clarify-v2-intent-to-plan/step-1/handoff.md`, run before any edit: exit 0, 4 pre-edit controls recorded red.
- `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`: PASS (209 checks), with every `ok: clarify: ...` line printed.
- (red) criterion 1, the selftest grep for all six `ok: clarify: <rule> ` lines: exit 0.
- (red) criterion 2, `plan_check.py clarify --text x`: exits 1 with `FAIL clarify-goal`, so the criterion passes (exit 0).
- (red) criterion 3, all 8 `.ask.md` files non-empty and all 8 `.expected.md` files passing `plan_check.py clarify --file`: exit 0.
- (red) criterion 4, 07 and 08 expected files are one line each with the right prefix: exit 0.
- (guard) scope diff against `SDLC_BASE_SHA=ad35eaaa04e635875c9db778c0a741ee5319421b`: exit 0, no out-of-scope path.
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0. No criterion names it; I ran it because the handoff says items 42, 43 and 49 apply to these files.
- `git diff --check`: exit 0. Also unnamed, run for the same reason.

## Notes
- `report()` is unchanged: it already prints `ok: clarify plan passes` for any kind other than `plan`.
- The pass-through rule returns early. When the first non-empty line has the prefix and more lines follow, only `clarify-pass-through` is reported, which keeps its mutant flagged as exactly that rule.
- In the `clarify-done-defect` rule, `verifier result` matches in any letter case. The handoff did not say which case to match.
- A fixed sha is a hex token of 7 to 40 characters with at least one digit and one letter a-f. A token after `$` or touching another word character is not counted, so `$SDLC_BASE_SHA` and words like "facade" pass; a selftest case covers this.
- The `Done when:` line may be bulleted (`- Done when:`), but then its items must be indented under it. The item list stops at the first line that is not a `- ` item.
- Not every ask is a verbatim quote, and each `Source:` line says so.
  - `02-wrong-unit` is rebuilt from the T-0182 and T-0183 goal; the shipped unit was `supervisor.py`.
  - `08-follow-up` is the "any updates" phrase from the T-0448 intent.
  - `03-conflicting-ask` sets the T-0429 title against the "One independent verifier per ticket" rule in the root AGENTS.md.
- The eval files use `${CLAUDE_PLUGIN_ROOT}/scripts/...` paths, not `plugins/...` paths. Each referenced script exists, and check.py item 42 passes.
- Three files the scope guard allows were left untouched because this step's Do does not name them: `skills/clarify/SKILL.md`, `skills/handoff-format/SKILL.md` and `adapters/codex/agents/`.

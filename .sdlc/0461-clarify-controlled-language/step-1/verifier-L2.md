<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 selftest has no FAIL and an `ok: clarify: <rule> ` line for the 7 new rules: pass. Evidence: ran the criterion body against the built tree, no MISSING lines, `plan_check selftest: PASS (252 checks)`. red-checkpoint.jsonl records this span red at base (exit 1, pre-edit).
- #2 skill drift labels and eval 09 and 10 labels in the selftest: pass. Evidence: all four `ok:` lines present; red-checkpoint records it red at base.
- #3 hedge text prints `FAIL clarify-hedge`: pass. Evidence: `plan_check.py clarify --text` printed `FAIL clarify-hedge: Goal holds the hedge word "maybe"`, rc=1. Red at base per red-checkpoint.
- #4 `vagueness` delta prints `FAIL clarify-delta`: pass. Evidence: the command printed `FAIL clarify-delta: ... - vagueness: the ask is fuzzy ...`. Red at base per red-checkpoint.
- #5 ten `.ask.md` exist and ten `.expected.md` pass the lint: pass. Evidence: loop printed no NOASK or FAILS; 09 and 10 each end with `Source: constructed for T-0461`. Red at base per red-checkpoint.
- #6 core.md names CLARIFY_VERBS, CLARIFY_HEDGE, plan_check.py: pass. Evidence: no MISSING; the diff adds a 4-line `## Controlled handoff words` section that copies neither list. Red at base per red-checkpoint.
- #7 SKILL.md holds the 11 literal strings: pass. Evidence: no MISSING. This span has no pre-edit control in red-checkpoint.jsonl (the builder disclosed it). I checked it myself: `git show 01a8cca7:plugins/sdlc-lite/skills/clarify/SKILL.md | grep -F` shows the base lacks `stopped: `, `category-mismatch` and `Do verbs: `, so the loop is red at base.
- #8 (guard) `Codex host` kept in SKILL.md: pass. Evidence: grep matched at SKILL.md line 8.
- #9 (guard) scope: pass. Evidence: `git diff --name-only 01a8cca7` plus untracked files outside `.sdlc` lists only plan_check.py, core.md and files under `skills/clarify/`; the filter prints nothing.

Extra checks:
- Negative controls on eval 10, which lints clean at rc=0. Each single-line mutation turns a specific rule red:
  - `Maybe fix` triggers clarify-hedge and clarify-do-verb.
  - `Tweak` triggers clarify-do-verb.
  - A defaulted delta with no `[U]` triggers clarify-default-source.
  - Lower-case `must not` in Constraints triggers clarify-rfc2119.
  - `MUST` in the Goal triggers clarify-rfc2119.
  - A `vagueness` type triggers clarify-delta.
  - A non-runnable Done-when triggers clarify-done.
- `CLARIFY_VERBS` and `CLARIFY_HEDGE` equal the handoff's lists (set compare; `etc` is stored as `etc.` too).
- Contract dependents: `ask/SKILL.md:17` and `open-questions/SKILL.md:16` read `(gap: ...; default: ...)`, and eval 04 keeps that literal form. Both skills are untouched.
- `plugins/sdlc-lite/scripts/check.py` rc=0. `prompt_lint.py` rc=0 with 0 errors. `git diff --check` rc=0.
- SKILL.md has no `docs/` link and no `plugins/` prose path (the grep found only `${CLAUDE_PLUGIN_ROOT}/` paths), 3 hard gates, and the identity line comes after the Codex host line and Arguments.
- Steelman of a possible fail on the missing criterion 7 control: the handoff's process-deviations rule applies to a `red-checkpoint` line in `process-deviations.md`. That file does not exist, and the criterion is red at base by my own check. Dropped.

## Out of scope changes
None. The 14 changed or new files are all in scope, and the guard confirms it. Edits under `.sdlc/` are run records.

## For the next attempt
None

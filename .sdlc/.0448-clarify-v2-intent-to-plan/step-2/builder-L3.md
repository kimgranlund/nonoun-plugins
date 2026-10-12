<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/clarify/SKILL.md: rewritten.
  - Gate: one-line `follow-up: ` and `already scoped: ` pass-throughs, and a changed ask means a re-run.
  - Extract, then Size and lane: `Level:` L1 to L4 from the level rubric, lane confirmed by `steps.py lane` through the ticket `size:`.
  - Resolve: one AskUserQuestion round, or `(gap: ...; default: ...)` when unattended.
  - Tracker: section 8.1 in the skill's own words, with `claimed_by:` and no second tracker.
  - Write it down: the Goal, Intent, Context and Constraints template, with the Intent order Literal ask, Level, Deltas, Do, Non-goals, Done when, Verify.
  - Done when rules (`unverifiable: `, `[owner: maintainer]`), the Outcome block for multi-step work, and the plan-doc format pointer. It ends with the `plan_check.py clarify --file` lint loop.
  - `## Low tier` (extract, default, write) and the `evals/README.md` pointer.
  - `Bash` added to `allowed-tools`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/plugins/sdlc-lite/skills/handoff-format/SKILL.md: line 122 now reads `Written by /clarify: literal ask, level, verify, deltas, do, non-goals, done when. Optional.`
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/docs/reports/2026-10-11-clarify-v2-replay.md: new replay report. It has one line per case, one `Result: 6 of 6 non-pass-through accepted, 2 of 2 pass-through one-line` line, the statement that a builder replay is not an independent model run, and a by-eye comparison.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/.sdlc/0448-clarify-v2-intent-to-plan/step-2/red-checkpoint.jsonl: written by redck.

## Checks
- `redck.py record .../step-2/handoff.md`, run before any edit: exit 0, 3 controls recorded red, marked retrospective (see Notes).
- (red) criterion 1, the 14-token grep loop on clarify/SKILL.md: exit 0.
- (red) criterion 2, the `sed -n "/^## Intent/,/^## Context/p" ... | grep -qF "level, verify"`: exit 0.
- Replay lint: `plan_check.py clarify --file` on all 8 replay outputs gave rc 0 and `ok: clarify plan passes` each time. Outputs 07 and 08 are 1 non-empty line each.
- (red) criterion 3, the `^Result: ...` regex over `docs/reports/*-clarify-v2-replay.md`: exit 0. The report has exactly 1 `Result:` line.
- (guard) scope diff against `ad35eaaa04e635875c9db778c0a741ee5319421b`: exit 0, no out-of-scope path.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: exit 0 ("19 role levels, 9 agents, 22 generated definitions checked").
- (guard) `python3 scripts/check-packaging.py`: exit 0 (PASS).
- (guard) `codex_roles.py generate --check && claude_roles.py generate --check`: exit 0.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite docs/reports`: exit 0. The untracked report was also checked with `git diff --no-index --check`, which printed no findings.
- `python3 plugins/sdlc-lite/scripts/docs_check.py`: 0 errors, 24 warnings, none in the new report.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 after 939 s. The log is at /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/.worktrees/tmp/0448-s2-builder-L3/check.log.

## Notes
- redck ran before the first edit but stored its record as retrospective. Step 1's uncommitted work (plan_check.py, evals/) already differed from `$SDLC_BASE_SHA`, so redck called it "a base control". It is not a run made after editing.
- How the replay ran:
  - Each of the 8 cases ran in its own fresh-context Claude sub-agent, Sonnet at default effort, spawned by this builder.
  - Each was told to skip the Tracker section and `steps.py lane`, read no eval file except its own ask, and write only to /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/f/.worktrees/tmp/0448-s2-builder-L3/replay/0{1..8}-*.md. That folder is gitignored and left in place so the verifier can lint the outputs again.
  - `git status` afterwards showed no new files in the tree.
  - `$SDLC_TMP_WORKTREES` was unset, so the brief's tmp prefix was used.
- The step 1 `.expected.md` files write `Level:` with commas. The skill now uses the handoff's `Level: L<n> (lane: ...; cost: ...; reversible: ...)` shape, and the lint accepts both. The evals were not edited because this step's Do does not name them; the planner may want a follow-up to align them.
- Two Level estimates differ by eye from the expected files: 05 is L2 against L4 expected (it read the source as a design-only pass), and 06 is L3 against L2. The report records both. The lint checks shape only.
- `agents/conductor.md` was not touched, so `codex_roles.py generate` was not needed. The four dependents that route to clarify by name are unchanged, as the handoff said.

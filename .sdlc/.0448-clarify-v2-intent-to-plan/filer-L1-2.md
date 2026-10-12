<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective, step 2: attempt 7b55bee9c52948dba42febcf9d5262ea, handoff sha256 cd653eec9c1c, 3 of 3 (red) criteria without a pre-edit red control. They are the 14-token grep loop on `clarify/SKILL.md`, the `sed -n "/^## Intent/,/^## Context/p"` check on `handoff-format/SKILL.md`, and the `^Result:` regex loop over `docs/reports/*-clarify-v2-replay.md`. `redck.py record` ran before the first edit, but step 1's uncommitted work already differed from the base sha, so it stored the record as retrospective. The verifier then ran the controls against base `ad35eaaa` and all three were red there. A passing verdict does not clear the deviation.
- process deviation: red-checkpoint: retrospective, step 3: attempt 5c1aab833596477f9087771a157e32ce, handoff sha256 efed94dad57d, 1 of 1 (red) criteria without a pre-edit red control. It is the loop over `clarify/evals/0[1-6]-*.expected.md`. `redck.py` found 21 source paths already differing from base, so no pre-edit record was taken. The eval files are untracked, so the old line 10 cannot be recovered from git. The verifier built its own negative controls instead: copies of the six files with line 10 rewritten to the old shapes made the criterion grep return 1 on all six, and deleting the `Level:` line from a copy of 01 made `plan_check.py clarify --file` exit 1 with `FAIL clarify-level`. The claims "change nothing else" and "keep each file's level number" rest only on the builder's note, because there was nothing to diff against.
- The "6 of 6" replay count is the builder's claim and is not independently confirmed. The builder spawned one Sonnet sub-agent per case, so the replay was not an independent model run. The replay outputs under `.worktrees/tmp/0448-s2-builder-L3/replay/` no longer exist. The verifier only checked the report line's format and re-linted the 8 `.expected.md` files, not the replay outputs.
- All three steps passed verification: step-1 verifier-L2, step-2 verifier-L2 and step-3 verifier-L1 each returned pass.

## PR title
T-0448: Modernize clarify: plan-ready intent block, runnable done-when, `plan_check.py clarify` lint

## PR body
Summary
- `/sdlc-lite:clarify` now turns a fuzzy ask into a plan-ready intent block in one pass. The block is Goal, Intent and Context, with a size and lane estimate and a runnable Done when.
- A new `plan_check.py clarify` lint checks that block. Eight eval cases built from asks in this repo's history sit under the skill folder, and their `Level:` lines match the skill's shape.

Changes
- `plugins/sdlc-lite/scripts/plan_check.py`:
  - New `clarify` kind with `check_clarify`, six rules and a selftest. The rules cover goal, non-goals, level, a runnable or `unverifiable:` Done when, the three Done when defects, and one-line pass-through.
  - The three defects are a criterion that reads its own step's verifier result, one that names a fixed sha, and one that needs a live rehearsal without `[owner: maintainer]`.
  - One-line pass-through is `already scoped: ` or `follow-up: `.
- `plugins/sdlc-lite/skills/clarify/SKILL.md`, rewritten:
  - Gate, pass-throughs and re-run on a changed ask.
  - Size and lane estimate (`Level` L1 to L4, confirmed by `steps.py lane`) with a one-line cost and reversibility note.
  - One question round, or `(gap: ...; default: ...)` when unattended.
  - Tracker step per lane-lifecycle section 8.1.
  - Done when rules and the Outcome block for multi-step work.
  - A three-step `## Low tier` path (extract, default, write).
  - A closing lint loop.
  - `Bash` added to `allowed-tools`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the Intent line now lists "level, verify".
- `plugins/sdlc-lite/skills/clarify/evals/`: 8 ask and expected pairs plus a README. Step 3 rewrote line 10 of cases 01 to 06 to the skill's `Level: L<n> (lane: ...; cost: ...; reversible: ...)` shape. The old lane word `chain` became `full` in 02 and 05, and level numbers are unchanged.
- `docs/reports/2026-10-11-clarify-v2-replay.md`: the replay report.

Verification
- Step 1 (verifier-L2 pass):
  - `plan_check.py selftest` passes with 209 checks and an `ok: clarify:` line per rule.
  - `clarify --text x` exits 1 with `FAIL clarify-goal`.
  - All 8 `.expected.md` files pass `clarify --file`.
  - The two pass-through files are one line each.
  - The verifier disabled the live-rehearsal branch in a throwaway copy, and the selftest then failed on that rule.
- Step 2 (verifier-L2 pass):
  - The skill token loop, the handoff-format line and the replay report line were each red at base.
  - The scope diff, `check.py`, `check-packaging.py`, the `codex_roles.py` and `claude_roles.py` `generate --check` runs, `git diff --check` and `bash plugins/sdlc-lite/scripts/check.sh` all exit 0.
- Step 3 (verifier-L1 pass):
  - Every `0[1-6]-*.expected.md` has the new `Level:` shape and passes `plan_check.py clarify --file`. The criterion loop exited 0.
  - The scope guard exited 0. Tracked changes are only `plan_check.py`, `clarify/SKILL.md` and `handoff-format/SKILL.md`.
  - The verifier's own negative controls made the shape check and the lint go red.
- Replay: 6 of 6 non-pass-through outputs were accepted by the lint, and both pass-through outputs were one line. This is a builder replay with Sonnet sub-agents, not an independent run, and the outputs were not preserved.
- Process deviations: steps 2 and 3 recorded their red controls retrospectively, as described under Warnings. The step 2 verifier re-ran its controls against base and found them red. The step 3 verifier used its own negative controls because the eval files are untracked.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- clarify: the skill now writes a plan-ready intent block (goal, non-goals, level and lane, runnable Done when). It passes one-line follow-ups and already-scoped asks through unchanged. It has a three-step low-tier path.
- plan_check.py: new `clarify` kind lints that block. It refuses a Done when that reads its own verifier result, names a fixed sha, or needs a live run without `[owner: maintainer]`.
- clarify/evals/: 8 eval cases built from asks in this repo's history.

## Follow-ups
- note: The 6 of 6 replay result was not independently confirmed. The builder's replay outputs were not preserved, and a rerun by an independent model would settle it.
- note: The replay is a builder run with Sonnet sub-agents that skipped the Tracker section and `steps.py lane`, so those two parts of the new skill have no replay evidence.
- note: In the replay, case 05 came out at L2 against the expected L4 and case 06 at L3 against the expected L2. The lint checks shape only, so level calibration of the skill is unmeasured.

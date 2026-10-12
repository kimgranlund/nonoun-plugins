<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt 7b55bee9c52948dba42febcf9d5262ea, handoff sha256 cd653eec9c1c, 3 of 3 (red) criteria without a pre-edit red control: the 14-token grep loop on `clarify/SKILL.md`; the `sed -n "/^## Intent/,/^## Context/p"` check on `handoff-format/SKILL.md`; and the `^Result:` regex loop over `docs/reports/*-clarify-v2-replay.md`. This is step 2. `redck.py record` ran before the first edit, but step 1's uncommitted work already differed from the base sha, so it stored the record as retrospective. The verifier then ran the controls itself against base `ad35eaaa`: all three are red there. A passing verdict does not clear the deviation.
- The "6 of 6" replay count is the builder's claim and is not independently confirmed. The replay was not an independent model run: the builder spawned one Sonnet sub-agent per case. The replay outputs under `.worktrees/tmp/0448-s2-builder-L3/replay/` no longer exist. The verifier checked only the report line's format. It re-linted the 8 `.expected.md` files, not the replay outputs.
- Both steps passed verification (step-1 verifier-L2: pass, step-2 verifier-L2: pass).

## PR title
T-0448: Modernize clarify: plan-ready intent block, runnable done-when, `plan_check.py clarify` lint

## PR body
Summary
- `/sdlc-lite:clarify` now turns a fuzzy ask into a plan-ready intent block in one pass. The block is Goal, Intent and Context, with a size and lane estimate and a runnable Done when.
- A new `plan_check.py clarify` lint checks that block, and 8 eval cases built from asks in this repo's history sit under the skill folder.

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
- `plugins/sdlc-lite/skills/clarify/evals/`: 8 ask and expected pairs plus a README. They are a bare goal, a wrong-unit ask, a conflicting ask, an already-scoped ask, a follow-up, an unattended gap, and others.
- `docs/reports/2026-10-11-clarify-v2-replay.md`: the replay report.

Verification
- Step 1 (verifier-L2 pass):
  - `plan_check.py selftest` passes with 209 checks and an `ok: clarify:` line per rule.
  - `clarify --text x` exits 1 with `FAIL clarify-goal`.
  - All 8 `.expected.md` files pass `clarify --file`.
  - The two pass-through files are one line each.
  - The verifier disabled the live-rehearsal branch in a throwaway copy, and the selftest then failed on that rule.
- Step 2 (verifier-L2 pass): the skill token loop, the handoff-format line and the replay report line were each red at base. The scope diff, `check.py`, `check-packaging.py`, the `codex_roles.py` and `claude_roles.py` `generate --check` runs, `git diff --check` and `bash plugins/sdlc-lite/scripts/check.sh` all exit 0.
- Replay: 6 of 6 non-pass-through outputs were accepted by the lint, and both pass-through outputs were one line. This is a builder replay with Sonnet sub-agents, not an independent run, and the outputs were not preserved.
- Process deviation: step 2's red controls were recorded retrospectively, as described under Warnings. The verifier re-ran the controls against base and found them red.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- clarify: the skill now writes a plan-ready intent block (goal, non-goals, level and lane, runnable Done when). It passes one-line follow-ups and already-scoped asks through unchanged. It has a three-step low-tier path.
- plan_check.py: new `clarify` kind lints that block. It refuses a Done when that reads its own verifier result, names a fixed sha, or needs a live run without `[owner: maintainer]`.
- clarify/evals/: 8 eval cases built from asks in this repo's history.

## Follow-ups
- fix-now: Align the 8 `plugins/sdlc-lite/skills/clarify/evals/*.expected.md` files with the skill's `Level: L<n> (lane: ...; cost: ...; reversible: ...)` shape. They still use the older comma-style `Level:` line, which the lint accepts.
- note: The 6 of 6 replay result was not independently confirmed. The builder's replay outputs were not preserved, and a rerun by an independent model would settle it.
- note: The replay is a builder run with Sonnet sub-agents that skipped the Tracker section and `steps.py lane`, so those two parts of the new skill have no replay evidence.

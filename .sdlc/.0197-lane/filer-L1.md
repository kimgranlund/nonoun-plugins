<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0197: steps.py lane, review_required(), and skips.md

## PR body
### Summary
Adds `steps.py lane <ticket dir>`, which prints `fix`, `lean` or `full` on the first line, then `reason:` and `read:` lines. It reuses one extracted `review_required()` function, so `lane` and `review` read the same mandatory conditions. Every call appends its result to the ticket's `skips.md`.

The plan went through plan review twice. Round 1 returned replan with two findings: the size read broke on a handoff with no front matter, and `handoff-format/SKILL.md` had no owner. Round 2 passed. All three steps passed their independent verifier.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`, step 1:
  - Added `review_required(plan, task_dir)`.
  - `review_action` and `lean_warnings` now call it.
  - Added a new `(r) review_required` selftest case.
- `plugins/sdlc-lite/scripts/steps.py`, step 2:
  - Added a `# --- lane ---` section (`lane_action`, `lane_record`, `record_lane`, `cmd_lane` and helpers), the `lane` subcommand, and the docstring entry.
  - The lane is decided at three points. Before planning, ticket size alone decides. After planning, step levels, merge steps, criteria count and scope allow-list entries decide. After any `## Plan review` line, a lean ticket becomes `full`.
  - A `full` already recorded in `skips.md` stays `full`.
  - Added 9 `(lane)` selftest cases.
  - `criteria_count`, `is_scope_span` and `repo_path_ok` are now shared with `lean_warnings` and `widen`.
- `docs/maintenance/sdlc-internals.md`: a `lane <task dir>` clause in the `scripts/steps.py` paragraph.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: a new `## Lane per ticket` section, so the Codex host skill now mentions `steps.py lane`.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: replaced the "no script computes the lane yet" line with the `steps.py lane` sentence.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added a `skips.md` line to the task-folder layout.

### Verification
- Step 1 verifier: pass.
  - The selftest exits 0 and prints the new `(r) review_required` label.
  - A mutation of the reason text turned that case red.
  - The inspect checks on `review_action` and `lean_warnings` pass.
- Step 2 verifier: pass.
  - All 13 criteria were run through `bash -c`, and the full selftest and `results.py selftest` pass.
  - The verifier mutated a temp copy (`LANE_MAX_STEPS=3` and `steps.py` removed from `LANE_CONTRACTS`) to check that the cases bite.
  - It also probed a missing directory (rc 1, one stderr line), a file path, a sticky `skips.md`, and an existing `## Lane` section.
- Step 3 verifier: pass.
  - The greps for the three skill edits would all be red at base.
  - `bash plugins/sdlc-lite/scripts/check.sh` passes (shellcheck was skipped because it is not installed).
  - `python3 scripts/check-packaging.py` passes.
  - `codex_roles.py generate --check` reports no drift.
  - `tickets.py --root .sdlc check` reports 208 tickets with the roadmap current.
  - `git diff --check` is clean.
- Negative controls from the handoff:
  - The L4 step giving `full` and the `## Plan review` line flipping a lean ticket to `full` have named selftest cases that the step 2 verifier passed.
  - The builder's own mutations also turned the selftest red.
  - The artifacts do not show these two controls run against the base.
- Not run: a live run of `steps.py lane` on a real ticket dir or on a Codex host.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `steps.py lane <ticket dir>`, which prints `fix`, `lean` or `full` with `reason:` and `read:` lines and appends each result to the ticket's `skips.md`. Extracted `review_required()` so `lane` and `review` share the same mandatory conditions. The Codex host skill, `chain`, `handoff-format` and the internals doc now describe it.

## Follow-ups
- note: no artifact shows `steps.py lane` run on a real ticket dir or a live Codex host; all evidence is selftests, temp dirs and static checks, so live evidence is left to T-0208.
- note: a repeated `lane` call appends a duplicate record line to `skips.md` (step 2 builder smoke run); T-0198's guard should expect this.

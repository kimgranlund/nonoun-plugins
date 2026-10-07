<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: the verifier family block now has a fallback. When `order.py newest "$dir" builder` prints nothing, it scans the direct `step-<n>` children (regex `^step-[0-9]+$`, compared with `10#`), runs `order.py newest` on each, and uses the result from the highest-numbered step that has one. The fallback has a comment naming `codex_roles.py resolve` as its Codex twin. The header "Family rules" paragraph gets the specified sentence, which includes `step-<n>.superseded-<k>`. All new code stays inside the `{ ... }` group.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: new `# Task dir: ` header paragraph, placed before the "Throwaway worktrees" paragraph. New task-dir block covering cases 1 to 8, placed right after the T-0108 skill-file check and before the plan-reviewer block. Fixtures go under `$repo/.sdlc/td` and are removed at the end. Every failure reads `fail "task dir: <reason>"`.
- `docs/references/sdlc-internals.md`: in the `scripts/run.sh` entry, "the Fable-never-verifies-Fable swap" is replaced with the specified verifier family rule text.

## Checks
- `bash -n` on run.sh and run-selftest.sh: OK.
- AC1 (superseded opus ignored, step-1 sonnet → `--model opus --effort medium`): PASS.
- AC2 (step-10 sonnet beats step-2 opus, L2 → `--model opus --effort high`): PASS.
- AC3 (guard, task dir's own opus build wins → sonnet medium): PASS.
- AC4 (guard, verifier at step-2 ignores step-1 → sonnet medium): PASS.
- AC5 (new selftest run against the base-SHA plugin copy): exits non-zero with `run selftest: FAIL: task dir: sonnet step build, verifier L1: want '--model opus --effort medium', got: ... --model sonnet --effort medium ...`. PASS. A first try failed only because I had appended `>&3` to the command myself. The verbatim command passes.
- AC6 (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS` (57.7 s).
- AC7 (run.sh header holds `step-<n>.superseded-<k>`): PASS.
- AC8 (selftest header has a line starting `# Task dir: `): PASS.
- AC9 (internals run.sh entry holds `step-<n>.superseded-<k>`): PASS.
- AC10 (only the three allowed files changed, no untracked files outside .sdlc): PASS.
- Extra: `git diff --check` clean. `python3 plugins/sdlc-lite/scripts/check.py`: ok, 19 role levels, 9 agents checked.

## Notes
- `/bin/bash` here is 3.2.57. The new code uses `[[ =~ ]]`, `[[ -d ]]`, `10#`, and `|| true` around the `order.py` substitution, with no 4.x features.
- The run.sh header now says `scripts/codex_roles.py resolve` applies the same rule on Codex, as the handoff specifies. That is not true until step 2 lands.

<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: new read-only `resume <task dir>` subcommand (`resume_action`, `cmd_resume`, `STEP_DIR_RE`); a module docstring entry and Usage line; an argparse subparser and dispatch; 7 selftest cases whose names start with `resume`.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: a resume rule at the start of section 4 (stale-attempt `run_lifecycle.py recover`, then inspect the step, then `steps.py resume`, never the newest or highest step dir). `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_lifecycle.py:*)` added to `allowed-tools`.
- `docs/references/sdlc-internals.md`: the `scripts/steps.py` entry gains a `resume <task dir>` clause, and its closing sentence now says /chain runs `resume` when it resumes a task.

## Checks
- Acceptance criteria 1 to 12, each run as written from the repo root with `SDLC_BASE_SHA=adf9ec1c…`: all rc=0. This covers the blocked step-2 fixture (prints `step-2` then `replan`), the all-passed fixture (`done`), the superseded dir plus step-10 fixture (`step-2` then `build L2`), the empty task dir (rc 1 with `steps resume:`), `selftest | grep '^ok: resume'`, the (guard) selftest, the three greps, the doc grep, and the (guard) scope diff.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: rc 0, `steps selftest: PASS` (176 ok lines, 7 of them `resume`).
- Negative control: the in-process selftest ran with `resume_action` monkeypatched to sort step numbers in reverse (newest/highest first). It failed as expected on "blocked step-2 is chosen over a later step-3" and on "superseded dir is ignored and step-2 comes before step-10".
- At base, in a throwaway worktree at `$SDLC_BASE_SHA` (since removed): `selftest | grep -c '^ok: resume'` printed 0, and `steps.py resume <dir>` gave an argparse invalid-choice error with rc 2. The new-behavior criteria are red at base as intended.
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0 (`ok: 18 role levels, 8 agents checked`).
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: rc 0 (`Codex agent definitions verified`).
- `git diff --check`: rc 0.

## Notes
- A `Fail` from `next_action` on a candidate is re-raised as one line, `steps resume: <task>/step-<n>: <next message>`, with its `steps next: ` prefix removed and any newlines joined into that line.
- On an all-done task, stdout is exactly two lines, `done` then `reason: every step-<n>/ passed`, with no path line. The chain SKILL text says a bare `done` means go to section 5.
- No live /chain run was done for the SKILL.md rule. Only the script behavior and the contract checks were exercised.

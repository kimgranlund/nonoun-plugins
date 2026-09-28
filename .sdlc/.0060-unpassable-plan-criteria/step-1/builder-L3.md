<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added `lint_steps(plan, steps)` plus helpers `criteria_lines`, `is_command`, `command_spans` and `lint_or_fail`. `split` now calls the lint right after `parse_steps` and refuses with `plan defect: replan this step (/chain 3)`. Also added the `lint` subcommand (`cmd_lint`, wired into `main`), the `BROKEN_CRITERION` and `BROKEN_PLAN` fixtures, selftest cases (j) to (m), and the docstring updates for `lint` and the new `split` refusal. `refused` gained an optional `needles=()` argument.
- `plugins/sdlc-lite/skills/plan/SKILL.md`: added `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)` to `allowed-tools`. Step 4 now runs `steps.py lint <result path>`, reports the outcome, and tells the user a refusal is a plan defect.
- `CLAUDE.md`: the `scripts/steps.py` bullet now covers the `plan defect` refusal under `bash -n` and says `lint <planner.md | task dir>` writes nothing.

## Checks
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0. Stdout has `ok:` lines for (j) (4 checks), (k), (l) and (m), then `steps selftest: PASS`.
- Negative control (`cd plugins/sdlc-lite/scripts && python3 -c "import steps; steps.lint_steps = lambda *a, **k: []; raise SystemExit(steps.selftest())"`): exit 1. Stderr lists only the three (j) checks that depend on the lint firing.
- The mktemp `BROKEN_PLAN` split command: printed `rc=1`. Stderr has `... step 1: acceptance criterion command does not parse: grep -c 'foo' bar'`, bash's error lines, and `plan defect: replan this step (/chain 3)`. `ls` shows only `handoff.md` and `planner-L2.md`, with no `step-1`.
- `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/0060-unpassable-plan-criteria/planner-L3.md`: exit 0, printed `steps lint: ok`.
- `python3 plugins/sdlc-lite/scripts/steps.py --help`: lists `{split,lint,selftest}` and has a `lint` help line.
- `grep -n 'scripts/steps.py' CLAUDE.md | grep -c 'plan defect'`: printed `1`. `grep -c 'steps.py lint' plugins/sdlc-lite/skills/plan/SKILL.md`: printed `1`.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0; shellcheck and plugin validate both ok.
- Extra check: I ran `lint` on all 42 `planner-*.md` files under `.sdlc/` and `plugins/sdlc-lite/bench/`. It flagged 3, each a span cut short by a backtick inside it, which matches the handoff's figure:
  - `followuptitle-in-tickets-py-returns/planner-L1.md` step 2
  - `ticket-intake-roadmap/planner-L2.md` step 3
  - `split-plan-into-steps/planner-L2.md` step 2

## Notes
- Two additions beyond the handoff's spec:
  - In (j), a second task-dir check: an older broken `planner-L3.md` next to a clean `planner-L2.md` that `runs.jsonl` names newest. `lint` must print ok there and `split` must succeed. This proves `lint` checks only the plan it picks, not every plan file.
  - (k) also asserts through `command_spans` that exactly the grep, python3 placeholder, env-prefixed and `$(...)` spans are kept, and the path, flag and prose spans are skipped. Without this, a lint that skipped everything would still pass (k).
- A `bash -n` timeout, which is not in the spec, becomes a finding instead of a traceback.
- The `M .sdlc/0060-unpassable-plan-criteria/handoff.md` in `git status` was already there before this step. I did not touch it.
- `.claude/agents/sdlc-lite-author.md` has no steps.py text that this change affects, so I left it alone.

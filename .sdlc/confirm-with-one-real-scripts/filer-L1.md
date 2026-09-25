<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0032: Confirm bench.sh --bench-dir reaches the headless /bench session

## PR body
### Summary
T-0025 left an open question: does `scripts/bench.sh --bench-dir DIR` actually pass DIR to the headless /bench session through `SDLC_BENCH_DIR`? One real run says it does, so no code change was needed. This PR adds only the task's `.sdlc/` records.

### Changes
- `.sdlc/confirm-with-one-real-scripts/probe.md` records the probe: its setup, the evidence it produced, and a negative control.
- `step-1/` holds the verifier result.
- No code files changed. The verifier ran `git status` and saw only `.sdlc/` artifacts.

### How it was verified
- **Probe setup:** a throwaway repo and a throwaway bench dir at `/tmp/benchprobe.RPim/bench`. The only task, `probe-greet`, exists in that dir and not in the plugin's `bench/tasks/`. Its hidden test fails on the base and passes on the solution.
- **Probe run:** `plugins/sdlc-lite/scripts/bench.sh --bench-dir /tmp/benchprobe.RPim/bench probe-greet`, launched from the worktree root, which has no `bench/`. It exited 0 and printed the summary row `pass 1 1 1 0.32`. Results and logs landed in the throwaway bench dir. The plugin's `bench/results/` listing was the same before and after the run.
- **Negative control:** with `SDLC_BENCH_DIR` unset, `bench-dir.sh` resolves to `plugins/sdlc-lite/bench`, and `probe-greet` does not exist there. The session could only have found the task through the variable that bench.sh exported.
- **Independent verifier (L1): pass on all 6 criteria.**
  - The task file exists only in the probe bench dir.
  - `grade.md` has `hidden_check: pass`, and the planner, builder and verifier outputs are present.
  - The plugin results listing diff is empty.
  - The negative control holds.
  - The wiring is where the probe says it is:
    - `bench.sh:22` sets `SDLC_BENCH_DIR` on the `claude -p` call.
    - `bench-dir.sh:17` honors that variable.
    - `skills/bench/SKILL.md:9` resolves the bench dir through `bench-dir.sh`.
  - The run log confirms the chain ran and the Sonnet verifier was swapped to Opus.
  - No stray probe worktree is left.
- **Verifier caveat:** it could not check `exit=0` or the 1m14s duration, because those went to stdout and not to the log. It judged this minor, since the grade file and the results show the run finished.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Confirmed with one real run that `scripts/bench.sh --bench-dir DIR` passes DIR to the headless /bench session through `SDLC_BENCH_DIR`. Results go to DIR, and the plugin's `bench/` is not touched. No code change. (T-0032)

## Follow-ups
- Have bench.sh write its exit code and wall-clock duration to the bench log: the T-0032 verifier could not check `exit=0` or the run time because both go only to stdout.

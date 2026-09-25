# Probe: bench.sh --bench-dir end to end (2026-09-24)

Verdict: pass. No code change needed.

## Setup
- Throwaway repo `/tmp/benchprobe.RPim/repo`: `greet.sh` base, solution adds an optional NAME arg; hidden test `test_greet.sh` is red on base, green on solution.
- Throwaway bench dir `/tmp/benchprobe.RPim/bench/tasks/probe-greet.md`. The task exists only there, not in the plugin's `bench/tasks/`.
- Command, from the repo worktree root (which has no `bench/`): `plugins/sdlc-lite/scripts/bench.sh --bench-dir /tmp/benchprobe.RPim/bench probe-greet`

## Evidence
- `exit=0` in 1m14s; summary row `2026-09-24-probe-greet  pass  1  1  1  0.32`.
- Results landed in `/tmp/benchprobe.RPim/bench/results/2026-09-24-probe-greet/` (grade.md `hidden_check: pass`, planner-L1, step-1 builder-L1 and verifier-L1) and the log in `/tmp/benchprobe.RPim/bench/logs/`.
- `plugins/sdlc-lite/bench/results/` listing is identical before and after.
- Negative control: without SDLC_BENCH_DIR, `bench-dir.sh` from the same cwd resolves `plugins/sdlc-lite/bench`, where `probe-greet` does not exist. So the session could only have found the task through the SDLC_BENCH_DIR that bench.sh exported.
- The probe's throwaway worktree was removed and pruned by /bench.

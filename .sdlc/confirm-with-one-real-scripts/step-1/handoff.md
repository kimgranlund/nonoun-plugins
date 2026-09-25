# Step 1: probe bench.sh --bench-dir end to end

level: L1 (probe run by the conductor; no code change)

## Goal
Prove with one real `plugins/sdlc-lite/scripts/bench.sh --bench-dir DIR` run that the headless /bench session resolves DIR through SDLC_BENCH_DIR.

## What was done
See `.sdlc/confirm-with-one-real-scripts/probe.md` for setup and claimed evidence. Artifacts are on disk under `/tmp/benchprobe.RPim/` (repo, bench/tasks, bench/results, bench/logs, before.txt = plugin results listing before the run).

## Acceptance criteria
1. `/tmp/benchprobe.RPim/bench/tasks/probe-greet.md` exists and `plugins/sdlc-lite/bench/tasks/probe-greet.md` does not.
2. `/tmp/benchprobe.RPim/bench/results/2026-09-24-probe-greet/grade.md` says `hidden_check: pass`, and the dir holds planner, builder, and verifier outputs from the run.
3. `ls plugins/sdlc-lite/bench/results` matches `/tmp/benchprobe.RPim/before.txt` (no result leaked into the plugin bench).
4. Without SDLC_BENCH_DIR and without --bench-dir, `plugins/sdlc-lite/scripts/bench-dir.sh` run from the repo root resolves to `plugins/sdlc-lite/bench` (so the task could only be found via the env bench.sh exports).
5. `plugins/sdlc-lite/scripts/bench.sh` exports `SDLC_BENCH_DIR="$bench"` to the `claude -p` call, and `skills/bench/SKILL.md` resolves BENCH via `bench-dir.sh`, which honors SDLC_BENCH_DIR.
6. Each claim in probe.md's Evidence section matches what is on disk.

Do not rerun bench.sh (it costs a model session); check the artifacts.

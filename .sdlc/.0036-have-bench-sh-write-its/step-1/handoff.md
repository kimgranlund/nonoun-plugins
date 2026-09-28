# Step 1: Write exit code and duration to the per-task log
level: L1
task: .sdlc/0036-have-bench-sh-write-its/handoff.md

## Goal
Each bench task's log file (`<bench>/logs/<date>-<task>.txt`) records that task's exit code and wall-clock duration, so a clean-context verifier can check `exit=0` and run time from the log alone.

## Constraints
bench.sh stays bash with `set -uo pipefail`, passes shellcheck, and keeps its CLI (`--bench-dir`, task args) and summary call unchanged. Non-goals: changing bench-summary.sh, runs.jsonl, the /bench skill flow, or task grading.

## Do
Edit `plugins/sdlc-lite/scripts/bench.sh`, inside the `for t in "$@"` loop:
- Before the claude call, set `log="$bench/logs/$(date +%Y-%m-%d)-$t.txt"` once and `start=$SECONDS`.
- Redirect the claude run to `>"$log"` instead of the inline `$(date ...)` path.
- Right after the claude call, capture `rc=$?` on the first line.
- Then `line="exit=$rc duration=$((SECONDS - start))s"`, then `echo "$line" >>"$log"` and `echo "$line"`.
- Replace the old `echo "exit=$?"`.
- Add one header comment line saying each task's log ends with an `exit=<code> duration=<N>s` trailer.
- Keep `set -uo pipefail`, the CLI, and the final bench-summary call unchanged.

Docs: add a short clause to CLAUDE.md (repo root) or `plugins/sdlc-lite/skills/bench/SKILL.md` only if a line there already describes what the per-task log holds; otherwise leave them alone.

## Acceptance criteria
- `grep -n 'date +%Y-%m-%d' plugins/sdlc-lite/scripts/bench.sh` matches exactly once (path computed once per task).
- Put a stub `claude` script that runs `exit 3` in a temp dir at the front of PATH, then run `PATH=$stub:$PATH plugins/sdlc-lite/scripts/bench.sh --bench-dir $tmp t1`. The tmp bench dir has `tasks/t1.md`, and bench-summary may fail. The last line of `$tmp/logs/*-t1.txt` matches `^exit=3 duration=[0-9]+s$`.
- Stdout of that run contains the same line `exit=3 duration=<int>s`.
- With the stub exiting 0, the log's last line is `exit=0 duration=<int>s`.
- `plugins/sdlc-lite/scripts/check.sh` passes (shellcheck included).

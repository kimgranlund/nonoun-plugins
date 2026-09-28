<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Make bench.sh append `exit=<code> duration=<N>s` to each task's log and echo the same line to stdout.

## Step 1: Write exit code and duration to the per-task log
level: L1
### Do
Edit `plugins/sdlc-lite/scripts/bench.sh`, inside the `for t in "$@"` loop (lines 20 to 26):
- Before the claude call, set `log="$bench/logs/$(date +%Y-%m-%d)-$t.txt"` once and `start=$SECONDS`.
- Redirect the claude run to `>"$log"` instead of the inline `$(date ...)` path.
- Right after the claude call, capture `rc=$?` on the first line.
- Then `line="exit=$rc duration=$((SECONDS - start))s"`, then `echo "$line" >>"$log"` and `echo "$line"`.
- Replace the old `echo "exit=$?"`.
- Add one header comment line saying each task's log ends with an `exit=<code> duration=<N>s` trailer.
- Keep `set -uo pipefail`, the CLI, and the final bench-summary call unchanged.

Docs: the CLAUDE.md Commands line for Benchmark and `skills/bench` describe the bench dir, not log contents. Add a short clause only if a line already describes what the log holds. Otherwise leave them alone. Grep found no such line.
### Acceptance criteria
- `grep -n 'date +%Y-%m-%d' plugins/sdlc-lite/scripts/bench.sh` matches exactly once (path computed once per task).
- Put a stub `claude` script that runs `exit 3` in a temp dir at the front of PATH, then run `PATH=$stub:$PATH plugins/sdlc-lite/scripts/bench.sh --bench-dir $tmp t1`. The tmp bench dir has `tasks/t1.md`, and bench-summary may fail. The last line of `$tmp/logs/*-t1.txt` matches `^exit=3 duration=[0-9]+s$`.
- Stdout of that run contains the same line `exit=3 duration=<int>s`.
- With the stub exiting 0, the log's last line is `exit=0 duration=<int>s`.
- `plugins/sdlc-lite/scripts/check.sh` passes (shellcheck included).

## Risks
- `bench-summary.sh` may need a populated bench dir in the stub run. Ignore its result and check only the log and stdout.
- Any consumer that parses the log's last line would now see the trailer. The handoff lists bench-summary as untouched, and it reads results and runs.jsonl, not the log.

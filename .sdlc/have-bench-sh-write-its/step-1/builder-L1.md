<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/bench.sh`: the log path is computed once per task, and the claude call redirects to `$log`. `rc=$?` is captured right after it. An `exit=<rc> duration=<N>s` line is appended to the log and echoed to stdout, replacing the old `echo "exit=$?"`. I added a header comment about the trailer.

## Checks
- `grep -c 'date +%Y-%m-%d'` on `bench.sh` gave 1. I counted rather than using `grep -n` and did not read the line number.
- With a stub `claude` that runs `exit 3`, the last log line and the stdout line were both `exit=3 duration=0s`.
- With the stub exiting 0, the last log line and the stdout line were both `exit=0 duration=0s`.
- `check.sh` passed. Only the last five lines of its output were shown: the three selftests, shellcheck and plugin validate all reported ok or PASS.

## Notes
- No doc line describes what the per-task log holds, so I left CLAUDE.md and the bench SKILL.md alone, as the handoff instructed.

<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/bench-dir.sh`: new executable resolver. It checks `--bench-dir`, then `$SDLC_BENCH_DIR`, then `<git top>/bench`, then the plugin's `bench/`. A missing value or an unknown option exits 2.
- `plugins/sdlc-lite/scripts/bench.sh`: takes an optional leading `--bench-dir`, resolves `$bench` through `bench-dir.sh`, and uses `$bench/` for logs and tasks. It passes `SDLC_BENCH_DIR="$bench"` to `claude -p`, calls `bench-summary.sh --bench-dir "$bench"`, and has an updated usage comment.
- `plugins/sdlc-lite/scripts/bench-summary.sh`: resolves the dir through `bench-dir.sh` (args passed through), loops over `"$bench"/results/*/`, has an updated header, and the cost pipeline now tolerates a run with no `runs.jsonl` (see Notes).

## Checks
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/*.sh`: exit 0.
- Temp git repo with `bench/`: prints `$t/bench` (proj-ok).
- Fallback from the repo root, from a temp git repo without `bench/`, and from a non-git temp dir: all print `<repo>/plugins/sdlc-lite/bench`.
- `--bench-dir /tmp/other` prints `/tmp/other`. `SDLC_BENCH_DIR=/tmp/envdir` prints `/tmp/envdir`. With both set, the flag wins (`/tmp/flag`).
- `bench-dir.sh --bench-dir` with no value exits 2 and prints the usage line. `--x` exits 2.
- `bench-summary.sh` from the repo root: output diffs identical to the pre-change output and lists the 5 `2026-09-24-*` rows.
- Temp bench with `results/2026-01-01-demo/grade.md`: both `--bench-dir` and `SDLC_BENCH_DIR` print one row, `2026-01-01-demo pass 0 0 0 0`.
- `grep -n 'root/bench'` on both scripts: no match. `SDLC_BENCH_DIR=` matches bench.sh line 22 (the `claude -p` env). `bench-summary.sh" --bench-dir` matches line 27.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
- One fix went beyond the listed changes. With `set -euo pipefail`, `bench-summary.sh` exited silently after the header when a result dir had no `runs.jsonl`, because `cat` failed inside the cost pipeline. That broke the demo-row acceptance criterion. I wrapped the `cat` in `{ ...; } || true`. Output for the existing runs is unchanged (diff identical).
- `bench-summary.sh` passes all of its args to `bench-dir.sh`, so an unknown arg exits 2.

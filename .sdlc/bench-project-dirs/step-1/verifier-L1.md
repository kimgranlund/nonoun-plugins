<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- shellcheck: pass. Evidence: `shellcheck --severity=warning scripts/*.sh` exited 0.
- Project bench wins: pass. Evidence: in a temp git repo with `bench/tasks/x.md`, `bench-dir.sh` printed `/private/var/.../tmp.Uk2ilB2mNK/bench`. That matches `pwd -P`/bench.
- Plugin fallback: pass. Evidence: run from the repo root, from a temp git repo with no `bench/`, and from a non-git temp dir. All three printed `<repo>/plugins/sdlc-lite/bench`.
- Explicit overrides: pass. Evidence:
  - `--bench-dir /tmp/other` printed `/tmp/other`.
  - `SDLC_BENCH_DIR=/tmp/envdir` printed `/tmp/envdir`.
  - With both the env var and `--bench-dir /tmp/flag`, it printed `/tmp/flag`, so the flag wins.
  - A relative `--bench-dir rel` was made absolute against the current dir.
- `--bench-dir` with no value exits 2: pass. Evidence: it printed the usage line and `exit=2`. `--x` also exited 2.
- Summary unchanged from repo root: pass. Evidence: it lists the 5 `2026-09-24-*` rows. `diff` against the HEAD version of `bench-summary.sh` (run under a fake root that symlinks `bench/` to the plugin's) showed no difference (`same`).
- Summary reads the resolved dir: pass. Evidence: with a temp dir holding `results/2026-01-01-demo/grade.md` (`hidden_check: pass`), both `--bench-dir <dir>` and `SDLC_BENCH_DIR=<dir>` printed exactly one row, `2026-01-01-demo pass 0 0 0 0`. The HEAD script has no such option and reads only `$root/bench`, so it would not print this row. The check can go red.
- Wiring greps: pass.
  - `grep -n 'root/bench'` on `bench.sh` and `bench-summary.sh` returned nothing (grep exit 1).
  - `bench.sh:22` has `SDLC_BENCH_DIR="$bench"` in front of `claude -p`.
  - `bench.sh:27` matches `bench-summary.sh" --bench-dir`.
- `scripts/check.sh` exits 0: pass. Evidence: exit 0. The selftest, tickets selftest, board selftest, shellcheck and plugin validate all passed.

## Out of scope changes
- The `cat` in `bench-summary.sh` is now wrapped in `{ ...; } || true` so a results dir with no `runs.jsonl` no longer aborts the script. The builder disclosed this. The demo-row criterion needs it, so I accept it.
- `.sdlc/bench-project-dirs/handoff.md` is modified (plan/ticket bookkeeping, not plugin code).
- Untracked `.sdlc` artifacts: `planner-L2.md`, `runs.jsonl`, `step-1/`, `step-2/`.

## For the next attempt
None

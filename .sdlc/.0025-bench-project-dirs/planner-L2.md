<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Resolve the bench dir with one shared rule, so a project's bench tasks, results and logs stay in the project and a plugin update never removes them. The rule: `--bench-dir DIR`, then `SDLC_BENCH_DIR`, then `<project>/bench/`, then the plugin's `bench/`.

## Step 1: Shared bench-dir resolver, wired into bench.sh and bench-summary.sh
level: L2
### Do
- Add a new executable file, `plugins/sdlc-lite/scripts/bench-dir.sh`. Usage: `bench-dir.sh [--bench-dir DIR]`. It prints one absolute path on stdout. The rules below apply in order, and the first match wins:
  1. `--bench-dir DIR` if given. A relative DIR is made absolute against the current dir.
  2. `$SDLC_BENCH_DIR` if set and non-empty. Make it absolute the same way.
  3. `<top>/bench` if `top=$(git rev-parse --show-toplevel 2>/dev/null)` succeeds and `<top>/bench` is a directory.
  4. The plugin's `bench` dir: `$(cd "$(dirname "$0")/.." && pwd)/bench`.
  
  A missing argument to `--bench-dir` or an unknown option exits 2 with a usage line on stderr. Bash 3.2 only: no associative arrays and no `mapfile`.
- Change `plugins/sdlc-lite/scripts/bench.sh`:
  - Parse an optional leading `--bench-dir DIR`. The remaining args are task names.
  - Set `bench="$("$root/scripts/bench-dir.sh" ...)"`, passing `--bench-dir` through when given.
  - Replace every `$root/bench/` path with `$bench/`: `mkdir -p "$bench/logs"`, the task `find` over `$bench/tasks`, and the log file `$bench/logs/<date>-<t>.txt`.
  - Run the `claude -p` call with `SDLC_BENCH_DIR="$bench"` in its env.
  - Call `"$root/scripts/bench-summary.sh" --bench-dir "$bench"`.
  - `--plugin-dir "$root"` stays as it is.
  - Update the usage comment.
- Change `plugins/sdlc-lite/scripts/bench-summary.sh`:
  - Accept an optional `--bench-dir DIR` and resolve through `bench-dir.sh` the same way.
  - Loop over `"$bench"/results/*/` instead of `"$root"/bench/results/*/`.
  - Update the header comment. Columns and output format do not change.
### Acceptance criteria
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/*.sh` exits 0.
- Project bench wins when it exists. Run `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/bench/tasks" && touch "$t/bench/tasks/x.md" && (cd "$t" && /abs/plugins/sdlc-lite/scripts/bench-dir.sh)`. It prints `$t/bench`; compare with `pwd -P` to avoid `/private` symlink differences.
- Plugin fallback. The same command run from the repo root, which has no `bench/`, prints `<repo>/plugins/sdlc-lite/bench`. The same fallback applies from a temp git repo with no `bench/`, and from a non-git temp dir.
- Explicit overrides:
  - In the temp repo that has `bench/`, `bench-dir.sh --bench-dir /tmp/other` prints `/tmp/other`.
  - `SDLC_BENCH_DIR=/tmp/envdir bench-dir.sh` prints `/tmp/envdir`.
  - With both the env var and the flag set, the flag wins.
- `bench-dir.sh --bench-dir` with no value exits 2.
- `plugins/sdlc-lite/scripts/bench-summary.sh` run from the repo root prints the same table as before the change. Compare its output with `git stash`-free `git show HEAD:plugins/sdlc-lite/scripts/bench-summary.sh | bash -s` run with the old root semantics, or check that it lists the 5 existing `2026-09-24-*` rows.
- Summary reads from the resolved dir. Create a temp bench dir holding `results/2026-01-01-demo/grade.md` with the text `hidden_check: pass`. Then `bench-summary.sh --bench-dir <that dir>` prints exactly one data row, `2026-01-01-demo` with `pass`. With `SDLC_BENCH_DIR=<that dir>` it prints the same row.
- bench.sh never runs a model to prove its wiring. `grep -n 'root/bench' plugins/sdlc-lite/scripts/bench.sh plugins/sdlc-lite/scripts/bench-summary.sh` returns nothing. `grep -n 'SDLC_BENCH_DIR=' plugins/sdlc-lite/scripts/bench.sh` shows the env passed to `claude -p`. `grep -n 'bench-summary.sh" --bench-dir' plugins/sdlc-lite/scripts/bench.sh` matches.
- `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Step 2: /bench skill and docs use the resolved bench dir
level: L1
### Do
- In `plugins/sdlc-lite/skills/bench/SKILL.md`:
  - Add a first instruction: before any `cd`, resolve the bench dir once from the session's starting directory with `BENCH=$(${CLAUDE_PLUGIN_ROOT}/scripts/bench-dir.sh)`. That honors `SDLC_BENCH_DIR` as set by `bench.sh`, then `<project>/bench/`, then the plugin's `bench/`. Keep the absolute path for the rest of the run.
  - Replace `${CLAUDE_PLUGIN_ROOT}/bench/tasks/<name>.md` with `$BENCH/tasks/<name>.md`, and point the format reference at `$BENCH/tasks/README.md` or the plugin's `bench/tasks/README.md`.
  - In step 5, replace `${CLAUDE_PLUGIN_ROOT}/bench/results/...` with `$BENCH/results/...`.
  - The summary call becomes `${CLAUDE_PLUGIN_ROOT}/scripts/bench-summary.sh --bench-dir "$BENCH"`.
- In `plugins/sdlc-lite/skills/board/SKILL.md` line 10, change "`bench/results` for benchmark runs" to "`<bench dir>/results` for benchmark runs (see `scripts/bench-dir.sh`)".
- In repo-root `CLAUDE.md`, extend the Benchmark line under Commands. The line should say:
  - The bench dir (tasks, results, logs) resolves in this order: `--bench-dir DIR`, then `SDLC_BENCH_DIR`, then `<project>/bench/` (git toplevel), then the plugin's `bench/`, via `scripts/bench-dir.sh`.
  - This repo's root has no `bench/`, so the dev bench stays at `plugins/sdlc-lite/bench/`.
- In `plugins/sdlc-lite/bench/tasks/README.md`, add one line: a project keeps its own tasks in `<project>/bench/tasks/`, which `/bench` prefers over the plugin's.
- `.claude/agents/sdlc-lite-author.md` names no bench paths, so leave it unchanged. Line 25 still holds as written.
### Acceptance criteria
- `grep -n 'CLAUDE_PLUGIN_ROOT}/bench' plugins/sdlc-lite/skills/bench/SKILL.md` returns nothing.
- `grep -n 'bench-dir.sh' plugins/sdlc-lite/skills/bench/SKILL.md` matches. The resolve instruction appears before the worktree `cd` step.
- `grep -n 'summary.sh --bench-dir' plugins/sdlc-lite/skills/bench/SKILL.md` matches.
- `grep -n 'SDLC_BENCH_DIR' CLAUDE.md` and `grep -n 'bench-dir.sh' plugins/sdlc-lite/skills/board/SKILL.md` both match.
- `grep -n '<project>/bench' plugins/sdlc-lite/bench/tasks/README.md` matches.
- No em dashes in any changed file: `git diff | grep '^+' | grep -c '—'` prints 0.
- `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Risks
- The headless `/bench` session may not see `SDLC_BENCH_DIR` if `claude -p` does not pass the env to Bash tool calls. It normally inherits the env. If it does not, the skill's resolver falls back to `<project>/bench`, which gives the same dir in the default case but loses an explicit `--bench-dir`. The verifier cannot prove this without a model call.
- The skill must resolve the dir before it `cd`s into the task worktree. The worktree's toplevel is the task repo, not the project, so resolving afterwards would pick the wrong `bench/`.
- `check.sh` shellchecks every script under `scripts/`, so the new `bench-dir.sh` must be clean.

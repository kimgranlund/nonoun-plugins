## Task goal
A project keeps its own bench tasks, results and logs, so a plugin update never removes them.

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

## Plan risks
- The headless `/bench` session may not see `SDLC_BENCH_DIR` if `claude -p` does not pass the env to Bash tool calls. It normally inherits the env. If it does not, the skill's resolver falls back to `<project>/bench`, which gives the same dir in the default case but loses an explicit `--bench-dir`. The verifier cannot prove this without a model call.
- The skill must resolve the dir before it `cd`s into the task worktree. The worktree's toplevel is the task repo, not the project, so resolving afterwards would pick the wrong `bench/`.
- `check.sh` shellchecks every script under `scripts/`, so the new `bench-dir.sh` must be clean.

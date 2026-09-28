<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0025: Bench tasks and results live in the project

## PR body
### Summary
Before this change, bench tasks, results and logs lived under `${CLAUDE_PLUGIN_ROOT}/bench/`. For installed users that path is the plugin cache, so a plugin update removed both the tasks and the run history. Now one shared rule picks the bench dir, in this order:
1. `--bench-dir DIR`
2. `SDLC_BENCH_DIR`
3. `<project>/bench/` (git toplevel), if it exists
4. the plugin's own `bench/`

Tasks, results and logs all live under that one dir. This repo's root has no `bench/`, so the dev bench stays at `plugins/sdlc-lite/bench/` with no flags.

### Changes
- `scripts/bench-dir.sh` (new): the resolver. It prints one absolute path. A relative path is made absolute against the current dir. A missing `--bench-dir` value or an unknown option exits 2.
- `scripts/bench.sh`:
  - Takes an optional leading `--bench-dir`.
  - Uses the resolved dir for tasks and logs.
  - Sets `SDLC_BENCH_DIR` for the headless `claude -p` session.
  - Calls `bench-summary.sh --bench-dir "$bench"`.
- `scripts/bench-summary.sh`:
  - Resolves the dir through `bench-dir.sh`.
  - Reads `"$bench"/results/*/`.
  - No longer exits silently when a result dir has no `runs.jsonl`. This fix was outside the plan: the builder reported it and the verifier accepted it.
- `skills/bench/SKILL.md`: resolves `BENCH` once, before any `cd` into the task worktree, and uses `$BENCH` for tasks, README, results and the summary call.
- `skills/board/SKILL.md`, repo `CLAUDE.md`, `bench/tasks/README.md`: updated to describe the resolve order and project-local tasks.

### Verification
Both steps got a pass verdict from an independent verifier.
- Step 1 (verifier L1):
  - shellcheck is clean.
  - A temp git repo with `bench/tasks/x.md` resolves to its own `bench/`.
  - The plugin fallback works from the repo root, from a temp git repo with no `bench/`, and from a non-git dir.
  - The flag overrides the env var, and the env var overrides the project dir.
  - A missing `--bench-dir` value exits 2.
  - Run from the repo root, `bench-summary.sh` gives the same output as the HEAD version.
  - A temp bench dir gives exactly one demo row through both `--bench-dir` and `SDLC_BENCH_DIR`.
  - The wiring greps match, and `scripts/check.sh` exits 0.
- Step 2 (verifier L1):
  - Every grep criterion passes, and each was checked against HEAD, where it fails.
  - The resolve instruction comes before the worktree `cd` (SKILL.md:9 vs :15).
  - No em dashes in the changed files.
  - `scripts/check.sh` exits 0.
- Not verified: whether the headless `/bench` session actually receives `SDLC_BENCH_DIR`. Proving it needs a model call. If the env var does not reach the session, the skill falls back to `<project>/bench`, which drops an explicit `--bench-dir`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Bench tasks, results and logs now live in the project. The dir resolves as `--bench-dir DIR`, then `SDLC_BENCH_DIR`, then `<project>/bench/`, then the plugin's `bench/` (new `scripts/bench-dir.sh`), so a plugin update no longer removes them. `bench-summary.sh` also no longer stops early on a result dir with no `runs.jsonl`.

## Follow-ups
- Confirm with one real `scripts/bench.sh --bench-dir DIR` run that the headless /bench session receives SDLC_BENCH_DIR, since without it the skill ignores an explicit --bench-dir.

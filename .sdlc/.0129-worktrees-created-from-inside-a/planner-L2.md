<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
At the end of every real run, run.sh reports each git worktree outside this run's own `$SDLC_TMP_WORKTREES` prefix, and each local branch, that appeared during the run. It prints one stderr line per item and adds `stray_worktrees` and `stray_branches` fields to the run's runs.jsonl line. It never removes anything and never changes the exit code.

## Step 1: Snapshot and report stray worktrees and branches in run.sh, with selftest coverage
level: L3
### Do
In `plugins/sdlc-lite/scripts/run.sh`:
- **Snapshot.** After the `SDLC_DRY_RUN` early exit and before the role runs (next to where `wt_tmp` is set), snapshot the worktree paths from `git -C "$toplevel" worktree list --porcelain` and the local branches from `git -C "$toplevel" for-each-ref --format='%(refname:short)' refs/heads`. A dry run takes no snapshot and prints nothing new.
- **Detection function.** Add a function that runs without errexit and never fails. It lists the worktrees now present that were not in the snapshot, leaving out any path under this run's prefix. Compare the prefix with the existing `phys` realpath logic, because macOS reports `/private/var` for `/var`. Each entry includes the worktree's branch when it has one. The function also lists the local branches not in the snapshot.
- **runs.jsonl fields.** When the runs.jsonl line is written after the role, add `stray_worktrees` (array of worktree paths) and `stray_branches` (array of branch names). Both are always present, and are empty arrays when nothing appeared. Pass them in with `jq --argjson`.
- **Stderr lines.** At exit, in `on_exit` after `cleanup_worktrees`, print one stderr line per item, once per run:
  - `run.sh: stray worktree appeared during this run: <path> [<branch>]` (leave out ` [<branch>]` for a detached worktree)
  - `run.sh: stray branch appeared during this run: <branch>`

  This also applies to a failed run (exit 1) and to exit 3.
- **Unchanged.** Exit codes, the required-section check, and the tmp-prefix cleanup stay as they are. Nothing is ever removed or deleted outside the prefix.
- **Header comment.** Update the header comment block, before `set -euo pipefail`. Describe the report, name the `stray_worktrees` and `stray_branches` fields, and say "appeared during this run". The report does not claim this role made the items, because concurrent fanout lanes and other role runs can add worktrees too.

In `plugins/sdlc-lite/scripts/run-selftest.sh`, extend the header comment and add cases, reusing the throwaway-repo and stub-claude pattern:
- A stub that makes a worktree outside the prefix and a branch from inside its own script is reported on stderr with both lines, and in runs.jsonl.
- A run that creates nothing prints no `stray` line and records empty arrays.
- A worktree under `$SDLC_TMP_WORKTREES` is never reported. Also assert that the existing `want_wt` runs print no `stray` line.
- A failing stub run (exit 1) that leaves a stray still reports it and still exits 1.
- A dry run stays silent. The existing exact-stderr `.nvmrc` dry-run checks already cover this.

Clean up any stray worktrees and branches the selftest makes inside its temp repos.

Do not edit `hooks/block-stray-worktree.sh` or `fanout.py`.
### Acceptance criteria
- `rs="$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/run.sh" && t=$(mktemp -d) && mkdir "$t/r" "$t/bin" && echo x >"$t/r/h.md" && git -C "$t/r" init -q && git -C "$t/r" add -A && git -C "$t/r" -c user.name=s -c user.email=s@e.invalid -c commit.gpgsign=false commit -q -m i && printf '%s\n' '#!/usr/bin/env bash' 'if [[ -n "${STRAY:-}" ]]; then git worktree add -q --detach "$SDLC_TMP_WORKTREES/w" HEAD; git worktree add -q --detach "$PWD-stray" HEAD; git branch stray-br; fi >/dev/null 2>&1' 'echo "{\"is_error\":false,\"result\":\"## Status\\ndone\",\"total_cost_usd\":0,\"duration_ms\":1,\"num_turns\":1}"' >"$t/bin/claude" && chmod +x "$t/bin/claude" && (cd "$t/r" && STRAY=1 PATH="$t/bin:$PATH" "$rs" builder L1 h.md >/dev/null 2>"$t/e1") && test "$(grep -c 'run.sh: stray worktree appeared during this run: .*r-stray' "$t/e1")" -eq 1 && ! grep -q '/.worktrees/tmp/' "$t/e1" && grep -qx 'run.sh: stray branch appeared during this run: stray-br' "$t/e1" && tail -1 "$t/r/runs.jsonl" | jq -e '(.stray_branches == ["stray-br"]) and (.stray_worktrees | length == 1) and (.stray_worktrees[0] | test("r-stray"))' >/dev/null && (cd "$t/r" && PATH="$t/bin:$PATH" "$rs" builder L1 h.md >/dev/null 2>"$t/e2") && ! grep -q stray "$t/e2" && tail -1 "$t/r/runs.jsonl" | jq -e '.stray_branches == [] and .stray_worktrees == []' >/dev/null`
- `grep -qF 'stray branch appeared during this run' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx 'run selftest: PASS'`
- `sed -n '/^set -euo/q;p' plugins/sdlc-lite/scripts/run.sh | grep -q 'stray_worktrees'`
- `sed -n '/^set -euo/q;p' plugins/sdlc-lite/scripts/run-selftest.sh | grep -qi 'stray'`
- `shellcheck plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`

## Step 2: Document the run-end stray report
level: L1
### Do
- **CLAUDE.md, `scripts/run.sh` bullet:** add one sentence about the run-end report. It covers the stderr line forms (quote `stray worktree appeared during this run`), the `stray_worktrees` and `stray_branches` runs.jsonl fields, that it is report only, that the exit code is unchanged, that this run's prefix is excluded, and that a dry run takes no snapshot.
- **CLAUDE.md, `hooks/block-stray-worktree.sh` bullet:** add that worktrees and branches made from inside a script or program a role runs bypass the hook, and that run.sh reports them at run end. Use the words `run end`.
- **`.claude/agents/sdlc-lite-author.md`:** make the same two notes. Extend the existing block-stray-worktree hazard line (the one containing `block-stray-worktree.sh`) with `run end`, and mention `stray worktree appeared during this run`.

Use no em dashes. Keep CLAUDE.md and the author agent in sync.
### Acceptance criteria
- `grep -qF 'stray worktree appeared during this run' CLAUDE.md`
- `grep -F 'hooks/block-stray-worktree.sh' CLAUDE.md | grep -qF 'run end'`
- `grep -qF 'stray worktree appeared during this run' .claude/agents/sdlc-lite-author.md`
- `grep -F 'block-stray-worktree.sh' .claude/agents/sdlc-lite-author.md | grep -qF 'run end'`
- `grep -qF 'stray_branches' CLAUDE.md`

## Step 3: Gates green
level: L1
### Do
Run `plugins/sdlc-lite/scripts/check.sh` and fix any red the earlier steps introduced (shellcheck, the run selftest, check.py doc guards). The `claude plugin validate` warning about CLAUDE.md is expected. Do not change `hooks/block-stray-worktree.sh`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- **Hook blocks for builders.** block-stray-worktree.sh fails closed on a Bash command that holds a heredoc or evaluator together with the words "git worktree add". Builders must write stub scripts with Edit/Write, or with single-quoted printf, and never with a heredoc in a Bash call. The step 1 fixture criterion passes the hook only because its `git worktree add` text sits inside single-quoted printf arguments; I confirmed that it runs on this host.
- **Concurrency.** A concurrent fanout lane or role run in the same repo will show up as a stray in the report. This is intended: the report says "appeared during this run".
- **Path forms.** The stray worktree path may print in `/private/var` form on macOS. The step 1 criterion therefore matches only on the `r-stray` basename.
- **Sync guards.** check.py may guard CLAUDE.md or author-agent phrasing that the step 2 edits touch. Step 3 catches any drift.

<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Document a tested recipe in the shared run operations that lets a conductor run a role from a clean temporary worktree when the primary checkout must not be touched, for example a bare-clone layout with a dirty primary worktree. The recipe states where the role's result and `.sdlc/` state land, and a stub-backed selftest in a throwaway bare-clone repository proves those locations and proves the primary worktree is left alone.

## Step 1: Write the temporary-worktree recipe in run operations
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add a section headed exactly `## Run a role from a temporary worktree` to `plugins/sdlc-lite/skills/handoff-format/run-operations.md`. It holds a numbered recipe with a fenced `sh` block and states these facts, which come from `plugins/sdlc-lite/scripts/run.sh`:
- When to use it: the project's checkout must not be touched, for example in a bare-clone layout (`<repo>.git` plus worktrees) where the primary worktree has uncommitted work. `run.sh` runs the role in the current directory and exits 2 outside a git work tree.
- Create: `wt="$(mktemp -d)/wt"`, then `git -C <any worktree or the bare repo> worktree add --detach "$wt" <commit>`. Use `--detach` so no branch is created. The path must be outside every existing worktree, so nothing is written into the dirty checkout.
- Run: `cd "$wt"` and run `run.sh <role> <level> <absolute path to .sdlc/<task>/.../handoff.md>`. The task's `.sdlc/<task>/` stays in its home, meaning the `.sdlc/` the conductor already uses for `/board` and `steps.py`. `run.sh` writes the following next to the handoff it is given, so they land in the home directory with nothing to copy back: `<role>-<level>.md`, `.log`, `runs.jsonl`, `*.attempt.json`, and, for builder and verifier, `base-sha`. If the home `.sdlc/` sits inside the checkout, it must be git-ignored there, as handoff-format already advises; otherwise the run dirties that checkout.
- Carry back code: a builder's edits exist only in `$wt`. Run the verifier for the same step in the same `$wt` before removal. To keep the work, commit it on a branch the recipe names (`git -C "$wt" switch -c <branch>`, then commit). Otherwise the work is discarded.
- Remove: `git -C <repo> worktree remove "$wt"` without `--force`, so a dirty worktree is refused instead of silently discarded. Then remove the `mktemp` parent. Remove only the path this recipe created. Never prune or remove other worktrees, branches, or stashes.
- Why the recipe does not reuse `SDLC_TMP_WORKTREES`: `run.sh` sets that prefix only inside one role run, under `<toplevel>/.worktrees/tmp/<role>-<pid>` of the checkout it runs in, and deletes it when that run exits. It therefore cannot hold a worktree that must outlive a builder run for the verifier, and it would sit inside the checkout that must not be touched. The run's own stray report does not flag `$wt`, because `$wt` exists before the run's snapshot.
- Scope: this is for interactive or headless conductors outside fanout. A fanout lane conductor already runs in a clean lane worktree and has `SDLC_ROLE=conductor`, so `hooks/block-stray-worktree.sh` denies this worktree add there.

In `plugins/sdlc-lite/skills/chain/SKILL.md`, extend the existing sentence that links shared run operations ("for readiness, attempt records, and safe recovery") so it also names `Run a role from a temporary worktree`, the section title verbatim. Do not change `fanout.py`. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`; if it reports drift, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.

Never write the text of a git worktree-add command into a Bash call (a criterion, a probe, a grep pattern), because inside a role run `hooks/block-stray-worktree.sh` denies it. Grep for `--detach` instead.
### Acceptance criteria
- `grep -q '^## Run a role from a temporary worktree' plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- `grep -qF -- '--detach' plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- `grep -qF 'worktree remove' plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- `grep -qF 'SDLC_TMP_WORKTREES' plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- `grep -qi 'bare' plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- `grep -qi 'fanout' plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- `grep -qF 'Run a role from a temporary worktree' plugins/sdlc-lite/skills/chain/SKILL.md`
- The new section states, in prose a reader can find, all four of these: the result and `runs.jsonl` land next to the absolute handoff path in the task's home `.sdlc/<task>/`; builder edits must be committed on a named branch before removal or they are lost; removal uses no `--force`; only the recipe's own worktree is removed.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`

## Step 2: Selftest the recipe in a throwaway bare-clone repository
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add a case to `plugins/sdlc-lite/scripts/run-selftest.sh`. Add a header comment paragraph starting `Temporary worktree recipe:` that describes the case, matching the style of the existing paragraphs. The case works inside the script's `$tmp`, reuses the stub `claude` on PATH, and makes no model call. It does the following:
1. Build a source repo with one commit that contains a tracked file and a `.gitignore` holding `.sdlc/`.
2. Run `git clone --bare` of it to `<tmp>/proj.git`, then add a primary worktree on the default branch and a second, unrelated user worktree.
3. Make the primary dirty: modify the tracked file and add an untracked file. Put a task handoff at `<primary>/.sdlc/t/handoff.md` with `## Goal`.
4. Snapshot the primary's `git status --porcelain` output, the tracked file's bytes, `git worktree list --porcelain` minus the recipe path, and `refs/heads`.
5. Run the step 1 recipe with the same command shapes the doc uses: a `mktemp` path, a detached worktree add from the bare repo, `run.sh scout L1 <absolute handoff>` from inside it, then a worktree remove without `--force`.
6. Assert all of these, calling `fail` with a reason for each miss:
   - `run.sh` exits 0.
   - `<primary>/.sdlc/t/scout-L1.md` and `<primary>/.sdlc/t/runs.jsonl` exist.
   - No result file appears anywhere under the temporary worktree path before removal.
   - After removal, the recipe path is absent from `git worktree list` and from disk.
   - The unrelated user worktree is still listed.
   - `refs/heads` is unchanged.
   - The primary's porcelain status and tracked-file bytes are byte-identical to the snapshot.
   - The primary has no `.worktrees` dir.

Before finishing, run a negative control and record it in the builder report: temporarily point the case at the primary instead of the temporary worktree, meaning `run.sh` runs from the primary, or the handoff is copied into the temporary worktree and removed with it. Show that the case fails with a `fail` reason, then restore it. This step proves the recipe with a stub backend only; a live model run is not part of it.

Never write the text of a git worktree-add command into a Bash call outside the script file, because `hooks/block-stray-worktree.sh` denies it inside a role run. Running `bash plugins/sdlc-lite/scripts/run-selftest.sh` is allowed.
### Acceptance criteria
- `grep -qF 'Temporary worktree recipe' plugins/sdlc-lite/scripts/run-selftest.sh && grep -qF 'clone --bare' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `out=$(bash plugins/sdlc-lite/scripts/run-selftest.sh 2>&1) && printf '%s\n' "$out" | tail -1 | grep -qx 'run selftest: PASS'`
- The builder report shows the negative control: the command it ran with the case pointed at the primary or at an in-worktree handoff, the resulting `run selftest: FAIL: <reason>` line naming the recipe case, and the restore.
- (guard) `command -v shellcheck >/dev/null && shellcheck --severity=warning plugins/sdlc-lite/scripts/run-selftest.sh`

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 and 2 introduced, in `plugins/sdlc-lite/skills/handoff-format/run-operations.md`, `plugins/sdlc-lite/skills/chain/SKILL.md`, `plugins/sdlc-lite/scripts/run-selftest.sh`, or generated Codex agents via `codex_roles.py generate`. A gate already red at the build-start HEAD is reported as `inherited red`. `check.sh` takes about 90 seconds.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`

## Risks
- Where the state lives is a design choice this plan makes: the `.sdlc/` home stays put, and the role gets an absolute handoff path. If the user's gen-ui-kit layout keeps a committed (not ignored) `.sdlc/` inside the dirty primary, every run still dirties that primary. The recipe states this condition, but the user may prefer a `.sdlc/` home outside every checkout.
- The ticket's "runs end to end" is proven with the stub `claude`, which exercises all of `run.sh`, but no model call is made. A live scout L1 run in a throwaway bare-clone repository is left for the conductor at close if the user wants live evidence.
- `hooks/block-stray-worktree.sh` denies any Bash call whose text contains a git worktree-add command inside a role run, including builder probes and verifier criteria. The criteria avoid that text, but a builder that echoes the recipe into a Bash call will be blocked.
- A headless conductor under fanout (`SDLC_ROLE=conductor`) cannot use the recipe, because the hook denies it. The doc scopes the recipe out of fanout lanes rather than changing the hook.

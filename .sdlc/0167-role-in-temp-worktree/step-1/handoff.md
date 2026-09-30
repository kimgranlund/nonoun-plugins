## Task goal
A conductor in a repository whose checkout must not be touched, such as a bare-clone layout with a dirty primary worktree, knows how to run a role from a clean temporary worktree and where `.sdlc/` state lives while it does.

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

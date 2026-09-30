<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0167: Document running a role from a temporary worktree

## PR body
### Summary
A conductor in a repository whose checkout must not be touched (for example a bare clone with a dirty primary worktree) can now run a role from a clean temporary worktree. The recipe is documented in the shared run operations, and a stub-backed selftest exercises it in a throwaway bare-clone repo. No model call was made in the selftest, and `fanout.py` is unchanged.

### Changes
- `plugins/sdlc-lite/skills/handoff-format/run-operations.md`: new section `## Run a role from a temporary worktree`. It has a numbered recipe with a fenced `sh` block and covers:
  - when to use it;
  - a detached worktree created at a `mktemp` path outside every existing worktree;
  - running `run.sh` from inside that worktree with the absolute handoff path;
  - results and `runs.jsonl` landing next to that handoff in the task's home `.sdlc/<task>/`, so nothing is copied back;
  - a builder's edits living only in the temporary worktree, so they must be committed on a named branch before removal or they are lost;
  - removal without `--force`, and only of the worktree the recipe created;
  - why `SDLC_TMP_WORKTREES` is not reused;
  - fanout lanes are out of scope.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: the sentence linking shared run operations now also names `Run a role from a temporary worktree`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`:
  - a `Temporary worktree recipe:` header paragraph;
  - one added line in the shared stub `claude` that records the directory the role ran in (`pwd -P`);
  - a new case that:
    - builds a `git clone --bare` repo with a dirty primary worktree and an unrelated `user-work` worktree;
    - runs the recipe with `run.sh scout L1`;
    - asserts the result and `runs.jsonl` land in the primary's `.sdlc/t/`;
    - asserts the role ran in the temporary worktree;
    - asserts the temporary worktree is gone after removal;
    - asserts the user worktree, `refs/heads`, the primary's porcelain status and tracked-file bytes are unchanged, and the primary has no `.worktrees` dir.

### Verification
- Step 1 (verifier pass):
  - Seven greps passed (heading, `--detach`, `worktree remove`, `SDLC_TMP_WORKTREES`, `bare`, `fanout`, and the `chain/SKILL.md` link).
  - The four required facts were read from the diff.
  - The `SDLC_TMP_WORKTREES` claim was checked against `run.sh`.
  - `codex_roles.py generate --check` passed.
  - The greps count 0 matches at the base SHA, so they can go red.
- Step 2 (verifier pass):
  - `run-selftest.sh` prints `run selftest: PASS`.
  - Two negative controls fail as intended. Running `run.sh` from the primary gives `FAIL: temporary worktree recipe: the role ran in ...`. Putting the handoff inside the temporary worktree gives `FAIL: ... scout-L1.md is missing`.
  - The verifier reran both in a scratch copy and added two more mutations (a changed tracked file, a primary `.worktrees` dir). All went red, and the unmodified copy stays green.
  - The shellcheck guard exits non-zero as written on the build host because shellcheck is not installed. With shellcheck 0.11.0 supplied through a temporary `pipx` shim, it passes with no findings, for both builder and verifier.
- Step 3 (verifier pass): `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`, `codex_roles.py generate --check`, and `git diff --check` against the base SHA (`.sdlc` excluded) all passed. `check.sh` skipped its shellcheck stage because shellcheck is not installed. No fixes were needed. The diff is three files, 105 insertions and 1 deletion.

### Limits
- The recipe is proven with the stub `claude`, which exercises all of `run.sh`. No live model run in a throwaway bare-clone repo was made.
- If a `.sdlc/` home inside the dirty primary is committed rather than git-ignored, every run still dirties that primary. The recipe states this condition.

## Changelog entry
- Documented a recipe for running a role from a clean temporary worktree when the primary checkout must not be touched (for example a bare clone with a dirty primary worktree). It covers where results and `.sdlc/` state land, committing builder work before removal, and safe removal. `run-selftest.sh` now covers the recipe with a stub-backed bare-clone case.

## Follow-ups
- decide: A live model run of the recipe (for example `scout L1`) in a throwaway bare-clone repo was not made, so the ticket's "runs end to end" is proven with the stub only; decide whether to require live evidence.
- decide: A committed (not git-ignored) `.sdlc/` inside a dirty primary still dirties that checkout on every run; decide whether to support a `.sdlc/` home outside every checkout.
- note: A headless conductor under fanout (`SDLC_ROLE=conductor`) cannot use the recipe because `hooks/block-stray-worktree.sh` denies the worktree add; the doc scopes it out and the hook was not changed.
- note: `shellcheck` is not installed on the build host, so `check.sh` skips its shellcheck stage and the literal shellcheck guard fails there; it was verified only through a `pipx` shim.

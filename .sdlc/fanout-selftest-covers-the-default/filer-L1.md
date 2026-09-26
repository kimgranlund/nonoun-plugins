<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0104: fanout selftest covers a full stub-driver run in the default lanes dir

## PR body
### Summary
`fanout.py selftest` only covered the default `.worktrees/fanout` lanes dir with `--dry-run`. It now also runs the stub driver end to end there, with no `--lanes-dir`. It checks that lane commits, merges and ticket closes leave `git status` clean in the main tree. `fanout.py run` behavior is unchanged. This is a follow-up from T-0090.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`: new selftest case 6 in `selftest()`. It uses a throwaway repo with `.worktrees/` git-ignored, two tickets on two lanes, the existing stub driver and `--gate true`. It asserts:
  - the run exits 0, and `report.md` shows every ticket `merged`;
  - each lane branch holds a commit with the subject `<id>: <title>`;
  - the integration branch has one `--no-ff` merge per ticket and holds each `<id>.txt`;
  - each ticket's handoff says `status: done` on the integration branch;
  - main's sha is unchanged and `HEAD` is still `refs/heads/main`;
  - `git status --porcelain --untracked-files=all` in the main repo is empty, with the output in the failure label so a stray file is named;
  - `git status --porcelain --ignored` lists `.worktrees/`, so the check is not vacuous;
  - `git worktree list` shows the lane and integration worktrees under `.worktrees/fanout/`.
- Module docstring: the `selftest` paragraph gains one sentence about the default lanes dir run.
- Nothing above the `# ---------- selftest ----------` marker changed except the docstring. `tickets.py`, `steps.py` and `board.py` are untouched.

### Verification
The verifier (L1) passed every criterion:
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` printed `fanout selftest: PASS`, and `plugins/sdlc-lite/scripts/check.sh` exited 0.
- Sabotage probe, stray file written only when the lanes dir is under `.worktrees/`: the selftest names `fanout-stray.txt`. The probe exits 1 at HEAD and 0 after the change.
- Sabotage probe, commit subject `<id> <title>`: the selftest fails and prints `got ['T-0001 Ticket a', 'fixture']`. The probe exits 1 at HEAD and 0 after the change.
- The docstring contains `default lanes dir`.
- The diff has two hunks, one in the docstring and one inside `selftest()`.
- The verifier read the diff and confirmed every listed assertion is present.

## Changelog entry
- fanout selftest: added a full stub-driver run in the default `.worktrees/fanout` lanes dir. It checks lane commits, merges and closes, and that `git status` in the main tree stays clean. `fanout.py run` is unchanged.

## Follow-ups
None

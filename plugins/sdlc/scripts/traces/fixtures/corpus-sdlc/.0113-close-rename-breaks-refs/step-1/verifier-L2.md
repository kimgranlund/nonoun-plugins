<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, committed file refuses and names `docs/spec.md`, nothing moves: pass. Evidence: the extracted span exited 0 in the tree. At HEAD, in a throwaway worktree, it exited 1, so the check can go red.
- Criterion 2, untracked file refuses: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- Criterion 3, `--reason` refuses: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- Criterion 4, `--rewrite-refs` rewrites the file to `.sdlc/.0001-x/handoff.md`, closes, and names the file in the output: pass. Evidence: exit 0 in the tree, exit 2 at HEAD (unknown flag).
- Criterion 5, `--dry-run --rewrite-refs` prints `rewrite docs/spec.md` and writes nothing: pass. Evidence: exit 0 in the tree, exit 2 at HEAD.
- Guard, `--force` closes and leaves the file: pass. Evidence: exit 0 in the tree and at HEAD.
- Guard, own-folder-only reference closes: pass. Evidence: exit 0 in the tree and at HEAD.
- Guard, plain slug never scans: pass. Evidence: exit 0 in the tree and at HEAD.
- Guard, outside git closes: pass. Evidence: exit 0 in the tree and at HEAD.
- Guard, `python3 plugins/sdlc/scripts/tickets.py selftest`: pass. Evidence: it prints `tickets selftest: PASS`.
- `grep -qF -- '--rewrite-refs' plugins/sdlc/scripts/tickets.py`: pass. Evidence: exit 0 in the tree. It was 1 at HEAD, where the file lacks the flag.
- Observable, new `(u) refs:` cases exist and deleting the scan call turns the selftest red: pass. Evidence:
  - The diff adds `(u) refs:` cases for the committed file, the untracked file, `--reason`, `--dry-run`, `--rewrite-refs`, `--reason --rewrite-refs`, the dry run with `--rewrite-refs`, `--force`, the own-folder and roadmap control, and the plain-mode control.
  - In a throwaway worktree I copied the tree's `tickets.py` in. The selftest printed PASS.
  - I replaced `outside_refs(root, slug) if archive else (...)` with `(None, '', '', [])`. The selftest then printed `tickets selftest: FAIL, these did not bite:`.
  - The worktree is removed and `git worktree list` shows only main and tickets-19.
- Extra check, `scripts/check.sh`: pass. Evidence: the last lines read `order/fanout/run/hook/hook live probe selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`. I did not capture the exit code, because I piped the output through `tail`.
- Builder claims accepted:
  - The builder's mutation and `check.sh` claims match my own runs above.
  - The refusal message drops `--force` when `--ack-warnings` is given, and `-I` skips binary files. Both are visible in the diff, in the `via_force` line and in the `git grep` arguments.

## Out of scope changes
None. `git status` shows only `plugins/sdlc/scripts/tickets.py` modified, which is the file the step names. The other entries are untracked `.sdlc/` task artifacts. The docstring and `Usage:` edits fall under Do item 4.

## For the next attempt
None

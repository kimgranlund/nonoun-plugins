<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: new. Has `run` (preflight, `--dry-run`, setup with rollback, one thread per lane, the `fcntl` merge lock, gates, close on the integration branch, `report.md`) and `selftest`.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/fanout.py" selftest || fail=1` and updated the header comment.
- `CLAUDE.md`: new `scripts/fanout.py` bullet in Layout. Also added "fanout" to the selftest list in the Commands line for `check.sh`.
- `.claude/agents/sdlc-lite-author.md`: added "fanout.py selftest" to the list of what `check.sh` runs (one-word sync edit).

## Checks
- `test -f plugins/sdlc-lite/scripts/fanout.py && python3 plugins/sdlc-lite/scripts/fanout.py selftest`: prints `fanout selftest: PASS`, exit 0. Ran it 6 more times in a row: PASS every time, about 7.5 s each.
- The `selftest()` reading criterion: it asserts all of these:
  - three merges on `fanout/test`
  - the red merge is undone: `T-0003.txt` and `RED` are absent, c is still `ready`, exit is 1, and the report says `red: test ! -e RED rc=`
  - main's sha is unchanged, HEAD is still main, and `status --porcelain` is empty
  - a, b and d are `done` on `fanout/test`
  - `T-0004.saw` lists `T-0001.txt`
  - T-0005 is `skipped` and there is no `T-0005.txt` (with a check that the alpha worktree and its `T-0003.txt` exist, so the absence check means something)
  - `board.py --lanes` lists alpha on `fanout/test-alpha` and beta on `fanout/test-beta`
  - `--dry-run` and the three refusals (duplicate id, unknown id, done ticket) exit 2 and leave no branch, worktree, lanes dir or dirty status behind
- Proof the selftest catches real bugs: I broke copies of the script one way at a time and each broken copy failed the selftest. The breaks were: no reset on red, no sync, no stop after a failure, no close, always exit 0, no duplicate-id check, done tickets allowed, and a dry run that sets up.
- Green-lane probe (verbatim, run from a script file): exit 0.
- Red-gate probe (verbatim): exit 0.
- Dry-run and refusal probe (verbatim): exit 0.
- `grep -q 'fanout.py" selftest' plugins/sdlc-lite/scripts/check.sh && grep -q 'fanout.py' CLAUDE.md`: exit 0.
- Guard `test -z "$(git branch --list 'fanout/*')" && ! git worktree list | grep -q -- '-fanout/'`: exit 0, checked again after all the selftest runs.
- Guard `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (all selftests PASS, shellcheck ok, plugin validate ok).
- Python 3.9: local `python3` is 3.9.6, and `ast.parse(feature_version=(3,9))` accepts the file.

## Notes
- Where the handoff left room, I chose these, and the docstring records each:
  - The pre-ticket sync takes the merge lock. Without it, a lane could pull in a merge whose gates later fail and get reset, and the selftest would be flaky.
  - The sync runs `git merge --ff --no-edit`, so a user-level `merge.ff` setting cannot add extra merge commits.
  - A lane stops at any outcome other than `merged`, including `merged, close refused`.
  - When the close is refused, the ticket folder in the integration worktree is cleaned with `git clean`. This stops a later `close` commit from picking up the copied files.
  - `BASH_*_TIMEOUT_MS` is set for every driver, not only the default one.
- Extra preflight refusals, all before anything is written:
  - lane names `integration` and `logs` (reserved)
  - a `--lanes-dir` inside the toplevel
  - an existing `<lanes-dir>/integration`
  - an integration branch that is already checked out in some worktree
  - branch-name clashes, such as an existing `fanout` branch blocking `fanout/<date>`
  - a ticket handoff that is not committed at the start commit (the post-setup check with rollback also stays)
- The refusal cases in the selftest pass `--driver 'exit 3'`. If a refusal ever stops refusing, the selftest can then never start a real `claude` run.
- Not done (outside this step): the default driver does not set `SDLC_ROLE`, so `hooks/block-publish.sh` does not guard the lane conductor. Only its prompt forbids pushing. Setting it would be a small follow-up if wanted.
- Step 1's uncommitted edits (`board.py`, `skills/board/SKILL.md`, the CLAUDE.md board bullet) were already in the tree, and this step uses them. Nothing was committed.

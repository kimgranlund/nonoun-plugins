<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `fanout.py` `run_ticket` stop a ticket whose lane tree is dirty before its sync. The ticket gets the outcome `dirty before sync` and the Commit cell `wip <sha7>`, so a `wip(<id>): dirty before sync` commit can never be merged into the integration branch. The selftest proves the guard with a case and a negative control, and the docs say so.

## Step 1: Guard the pre-sync wip commit, prove it in the selftest, fix the docs
level: L3
### Do
Reason for the level: this changes behavior inside the existing fanout architecture and needs a new end-to-end selftest case built on git fixtures.

1. `plugins/sdlc-lite/scripts/fanout.py`, `run_ticket`: keep the pre-sync `sha = wip_commit(wt, t.id, 'dirty before sync')` under the lock. When `sha` is non-empty, `say(...)` it as today, then `return 'dirty before sync', f'wip {sha}'` before the `git merge --ff` sync. Nothing else runs for that ticket: no sync, no driver, no lane commit, no merge. `run_lane` already stops the lane on any outcome other than `merged`, and marks later tickets `skipped`. Its own `wip_commit` then finds a clean tree and returns '', so `commit` keeps `wip <sha>` and the report's Commit cell shows it. When the tree is clean (`sha == ''`), the path must stay exactly as today. Update the comment above the call to say that the dirty work is set aside on the lane branch and the ticket stops, so that commit is never merged.
2. The same file, the module docstring:
   - Replace the sentence "Before each sync, a dirty lane tree is WIP-committed first." with one saying that a lane tree already dirty before a ticket's sync is committed as `wip(<id>): dirty before sync` on the lane branch, and that the ticket stops with the outcome `dirty before sync`: no sync, driver, lane commit, or merge.
   - Add a `selftest` paragraph for the new case 8 and its control.
3. The same file, `selftest()`: add case 8 after case 7, in its own temp subdirs.
   - Setup: a repo made with `make_repo` holding two ready tickets (T-0001, T-0002). One lane runs `alpha=T-0001,T-0002` with `--driver` set to the `STUB` script (`shlex.quote(str(stub))`, reusing the stub that case 1 writes) and `--gate "echo x >{lanes}/alpha/dirty.txt"`, where `{lanes}` is this case's lanes dir. That gate passes, so T-0001 merges, and it leaves the lane tree dirty before T-0002's sync. Driving this from a gate is how an end-to-end run can make a lane tree dirty before a ticket's sync, because fanout creates the lane worktree itself.
   - Every `expect` label starts with `dirty-sync case:`. The case asserts:
     - the run exits 1;
     - the report has the row `| alpha | T-0002 | dirty before sync | wip <sha7> |` (regex);
     - the tip subject of `fanout/<integ>-alpha` is exactly `wip(T-0002): dirty before sync`;
     - that tip is not an ancestor of the integration branch (`merge-base --is-ancestor` returns 1);
     - the integration branch holds `T-0001.txt` but not `dirty.txt`;
     - T-0002 is still `ready` on the integration branch;
     - main equals the fixture commit.
   - Negative control, with labels starting `dirty-sync control:`: the same two-ticket setup in fresh dirs, with no `--gate`. It exits 0, both tickets are `merged`, the lane tip subject does not start with `wip(`, and the integration branch holds `T-0002.txt`.
4. `plugins/sdlc-lite/skills/fanout/SKILL.md` line 9: replace "a dirty tree is also WIP-committed before each sync" with the new behavior: a tree dirty before a ticket's sync is WIP-committed as `wip(<id>): dirty before sync` and that ticket stops with the outcome `dirty before sync`, never merged.
5. The repo-root `CLAUDE.md`, the `scripts/fanout.py` bullet: rewrite "When a lane stops (...) and before a sync finds a dirty lane tree, the script commits the tree as `wip(<id>): <outcome>` ..." so that it covers the stop case as today, plus the pre-sync case: a lane tree dirty before a ticket's sync is committed as `wip(<id>): dirty before sync` and that ticket stops with the outcome `dirty before sync`. Both commits stay on the lane branch only and are never merged. Edit only that sentence; other lanes change this file.
6. `.claude/agents/sdlc-lite-author.md` does not describe the wip behavior today, so leave it unchanged.

Run formatters only on the files you changed.
### Acceptance criteria
- `d=$(mktemp -d) && F=$PWD/plugins/sdlc-lite/scripts/fanout.py && mkdir -p $d/r/.sdlc/a $d/r/.sdlc/b && for s in a:T-0001 b:T-0002; do printf -- '---\nid: %s\ntitle: "t"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\ng\n' "${s#*:}" >$d/r/.sdlc/${s%%:*}/handoff.md; done && export GIT_AUTHOR_NAME=x GIT_AUTHOR_EMAIL=x@x.invalid GIT_COMMITTER_NAME=x GIT_COMMITTER_EMAIL=x@x.invalid && git -C $d/r init -q -b main && git -C $d/r add -A && git -C $d/r -c commit.gpgsign=false commit -qm fixture && (cd $d/r && python3 $F run alpha=T-0001,T-0002 --integration fanout/p --lanes-dir $d/l --driver 'echo x >$FANOUT_TICKET.txt; printf "## Warnings\nNone\n\n## Follow-ups\nNone\n" >$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md' --gate "echo x >$d/l/alpha/dirty.txt" >/dev/null 2>&1; test $? -eq 1) && grep -qE '^\| alpha \| T-0002 \| dirty before sync \| wip [0-9a-f]{7} \|$' $d/l/report.md && test "$(git -C $d/r log -1 --format=%s fanout/p-alpha)" = "wip(T-0002): dirty before sync" && ! git -C $d/r merge-base --is-ancestor fanout/p-alpha fanout/p && ! git -C $d/r cat-file -e fanout/p:dirty.txt && git -C $d/r cat-file -e fanout/p:T-0001.txt` (run from the git toplevel; it writes only under a mktemp dir)
- `grep -qF "dirty-sync case:" plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "dirty-sync control:" plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS`
- `sed -n "1,/^import /p" plugins/sdlc-lite/scripts/fanout.py | grep -qF "dirty before sync"`
- `! grep -qF "Before each sync, a dirty lane tree is WIP-committed first" plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "dirty before sync" plugins/sdlc-lite/skills/fanout/SKILL.md`
- `! grep -qF "a dirty tree is also WIP-committed before each sync" plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -qF "dirty before sync" CLAUDE.md`
- `! grep -qF "and before a sync finds a dirty lane tree" CLAUDE.md`
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md`

## Step 2: Gates green
level: L1
### Do
Reason for the level: this step only runs the gate and makes small fixes to what step 1 changed.

Run `plugins/sdlc-lite/scripts/check.sh` from the git toplevel. It covers the fanout selftest, shellcheck, `claude plugin validate`, and the doc and table guards in check.py. Fix any red that step 1 introduced, and only in the files step 1 changed. If the gate was already red at the build-start HEAD, report Status `inherited red: <tests>`.
### Acceptance criteria
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS`

## Risks
- The handoff asks for a lane that is dirty "before its first ticket". An end-to-end run cannot do that, because fanout creates each lane worktree itself and nothing outside a driver or gate can write to it before the first sync. The plan uses a passing gate that dirties the lane before the second ticket's sync, which runs the same pre-sync code path. If the user needs the first-ticket case literally, it needs an in-process call to `run_ticket` against a pre-dirtied worktree.
- If `wip_commit` fails (add or commit error) on a dirty tree, it returns '' and the sync still runs as it does today. That can fail the sync, but nothing unmerged-by-contract gets merged.
- check.sh takes about 2 minutes. The step 1 behavior criterion runs a real fanout in a temp dir, about 5 to 10 seconds.

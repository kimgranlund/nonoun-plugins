## Task goal
fanout and solo_run open and close their lanes through `lanes.py`, so a merged lane's tree is gone after a run and a stopped lane stays with a report line.

## Step 3: prep, land, roll and settle use lanes; skill and reference text; gates green
level: L3
### Do
Depends on: step 2 (the sweep helper and the lane record in fanout).

Targets are `plugins/sdlc-lite/scripts/fanout.py` (`cmd_prep`, `print_prep`, `cmd_land` and `land_ticket`, `cmd_roll`, `cmd_settle`, the docstring and the selftest), `plugins/sdlc-lite/skills/fanout/SKILL.md` and `docs/references/sdlc-internals.md`.

1. prep:
   - Run the step 2 sweep helper after `refuse_overlap`, so a refusal still changes nothing.
   - For each solo dispatch, call `lanes.host_record(<id>-solo, branch=d['branch'], into=integration, tickets=[id], base=start, cwd=top)` and print `    host record: <path>`.
   - For a `full` lane's first ticket, replace the `tree: git worktree add -b ...` line with `tree: python3 <scripts>/lanes.py open <lane> --kind fanout --ticket <id>... --base <start> --into <integration> --path <tree> --branch <integration>-<lane> --no-claim`, listing all of the lane's ids.
   - Update prep's header line ("creates only ...") to name the host record.
2. land:
   - Host lane rebind (on `merged`): the host names the tree `agent-<agent_id>`, not `<id>-solo` (SKILL.md step 2, observed 2026-10-07). When the landed branch is checked out in a worktree under `<top>/.claude/worktrees/` whose leaf differs from `<id>-solo`, write `host_record(<leaf>, branch=<branch>, ...)` and remove the provisional `<lanes root>/host/<id>-solo.lane.json`. The host lane stays open; `dispatch.py prune --done` closes it (ticket C, T-0453).
   - Full lane close: when the branch's tree has a `.lane.json` of kind `fanout` and this ticket is the record's last ticket, close it after the merge lock is released with `lanes.close_lane(<tree>, into=<integration>, cwd=top)`. Print the close message, or `lane still open: <path> (<outcome>)`.
3. roll: at the end of every roll, after `roll_setup` succeeded and whatever the outcome, run `git worktree remove --force <lanes-dir>/rolling` and `git worktree prune`. The scratch tree is detached and holds no branch. `roll_setup` still creates it when absent.
4. settle: after the fast-forward, or when the branch is already merged, close the integration branch's worktree through `lanes.close_lane(<worktree path>, into=<current branch>, cwd)`. This writes the archive ref before any removal (a handoff constraint), and the `--force` removal no longer stops on an untracked copied `.sdlc/config`. Print its message. Any refusal (not a plugin lane, row 4 lanes still open, no worktree) prints `lane still open: <path or branch> (<outcome>)`, keeps the branch and exits 1. The diverged refusal (exit 2) is unchanged.
5. Selftest:
   - Case 28 gets label `case 28 settle archive`. Its integration trees live at `<lanes dir>/<n>/integration` with `merge.lock` and `logs/`, as fanout makes them. After settle, `refs/archive/<UTC date>/fanout/ff` and `.../fanout/hand` exist. A tree outside a lanes dir is kept with `lane still open` and exit 1.
   - Case 30 (`case 30 host record`): prep writes `<lanes root>/host/T-0001-solo.lane.json` with kind `host` and ticket T-0001. A land from a worktree under `.claude/worktrees/agent-x` rebinds it to `agent-x.lane.json`.
   - Case 31 (`case 31 roll scratch`): after a merged roll and after a refused roll, `<lanes-dir>/rolling` is absent and `git worktree list --porcelain` names no rolling tree.
   - Case 32 (`case 32 full lane close`): a tree opened with prep's printed `lanes.py open` line, landed for its last ticket, is gone with an archive ref, and its branch is deleted.
   - Update case 22's `worktree add -b fanout/p-alpha` expect (found with `git grep -n "worktree add -b fanout/p-alpha"`) to the `lanes.py open` line, and its "creates no file" expect to allow the host record.
6. `skills/fanout/SKILL.md`:
   - Replace "Lane worktrees stay after the run so they can be inspected." with a lifecycle paragraph. It covers: lanes open through `lanes.py`; each lane whose tickets all merged is closed after an archive ref `refs/archive/<date>/<branch>`; a stopped lane stays with `lane still open: <path> (<outcome>)`; the integration tree stays until main contains it; `run` and `prep` start with `lanes.py sweep --apply` unless `lane_sweep: off`; roll removes its scratch; `$SDLC_LANE_PORT` is set under `lane_ports:`.
   - Sub-agent step 5 says the full-lane tree is made with the `lanes.py open` command prep prints.
   - `## 5. Main`: after the user-approved `git merge --ff-only <integration>`, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py settle <integration>`, which closes the integration tree now. Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lanes.py sweep --apply`, which closes every other landed lane; a lane younger than `lane_min_age_hours` waits for a later sweep. Settle comes first because sweep's `recent` row keeps a tip made minutes ago (lanes.py docstring, the truth table).
   - Add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lanes.py:*)` to `allowed-tools`.
   - Keep every phrase `check.py` pins: `FANOUT_SKILL_PHRASES` (`Solo first`, `--max-lanes`, `--stagger`, `fanout.py prep`, `fanout.py land`, `` `Tree: <path>` ``, `.claude/worktrees/`), the long-run words (`interactive`, `run_in_background`, `notification`, `sleep`, `SDLC_HEADLESS`), and the inherited-red route text.
7. `docs/references/sdlc-internals.md`:
   - Line 147: replace "the worktrees stay for inspection" with the lifecycle sentence.
   - Line 141: prep "creates nothing and writes nothing" now writes the host record; settle "removes its worktree and deletes the branch" now closes through `lanes.close` with the archive ref first; land rebinds the host record and closes a full lane after its last ticket.
8. Fanout docstring: update the prep, land, roll and settle sections. The phrase "the worktrees stay for inspection" must be gone.
9. Gates: run every gate below and fix any red an earlier step introduced.
### Acceptance criteria
- (red) `for l in "case 28 settle archive" "case 30 host record" "case 31 roll scratch" "case 32 full lane close"; do grep -qF "$l" plugins/sdlc-lite/scripts/fanout.py || exit 1; done && python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (red) `! grep -qF "Lane worktrees stay after the run" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `grep -qF "lanes.py sweep --apply" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `grep -qF "lanes.py open" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `sed -n "/^allowed-tools:/p" plugins/sdlc-lite/skills/fanout/SKILL.md | grep -qF "scripts/lanes.py"`
- (red) `! grep -qF "the worktrees stay for inspection" plugins/sdlc-lite/scripts/fanout.py docs/references/sdlc-internals.md`
- (guard) `grep -qF ".claude/worktrees/" plugins/sdlc-lite/skills/fanout/SKILL.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- `out=$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc") && test -z "$(printf "%s\n" "$out" | grep -vxF -e plugins/sdlc-lite/scripts/lanes.py -e plugins/sdlc-lite/scripts/solo_run.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/skills/fanout/SKILL.md -e docs/references/sdlc-internals.md -e "")"`

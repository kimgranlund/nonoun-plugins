<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout38/n/plugins/sdlc-lite/scripts/fanout.py: the step's four command changes, the docstring and the selftest.
  - prep: calls `sweep_lanes` after the refusals. It also writes each solo ticket's host record through the new helpers `host_record_path` and `write_host_record`, then prints `    host record: <path>`.
  - prep, full lane: the `tree:` line is now the `lanes.py open ... --no-claim` command, and the header line names the host record.
  - land: new `land_lanes`, called from `cmd_land` after the merge lock is released. It rebinds the host record and closes a full lane after its last ticket.
  - roll: `cmd_roll` removes `<lanes-dir>/rolling` and runs `worktree prune` in a `finally`.
  - settle: `cmd_settle` closes through `lanes.close_lane` and prints `lane still open: ...` with exit 1 when the close refuses.
  - Docstring: prep, land and roll sections updated, a settle section added, and cases 28 and 30 to 32 described. The settle argparse description is updated too.
  - Selftest: case 28 rewritten (label `case 28 settle archive`). New cases 30 (`case 30 host record`), 31 (`case 31 roll scratch`, checked inside case 27) and 32 (`case 32 full lane close`). Case 22's `pf` expect and its "creates no file" expect are updated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout38/n/plugins/sdlc-lite/skills/fanout/SKILL.md: five changes.
  - `scripts/lanes.py` added to `allowed-tools`.
  - The lifecycle paragraph replaces "Lane worktrees stay after the run".
  - Sub-agent step 5 names the `lanes.py open` command.
  - `## 5. Main` adds settle, then `lanes.py sweep --apply`.
  - Sub-agent step 1's "It creates nothing" now names the dispatch and host records.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout38/n/docs/references/sdlc-internals.md: three paragraphs updated.
  - Sub-agent lanes paragraph: prep's sweep and host record, the full lane `tree:` line, land's rebind and full-lane close, and settle through `lanes.close_lane`.
  - Roll paragraph: the scratch tree is removed at the end of every roll.
  - Run paragraph: the lifecycle sentence replaces "the worktrees stay for inspection".

## Checks
- `redck.py record step-3/handoff.md`, run before the first edit: exit 0. It recorded 5 controls, all red, phase `retrospective` (see Notes).
- `SDLC_BASE_SHA` was empty in the shell, so I exported `92ce1efac3f7bcac41a82d655e8ff313b272b380` for the `git diff --check` and scope criteria.
- C1 was not run as one command:
  - The four label greps exit 0.
  - `fanout.py selftest` passed on its own (2:07). That run came before the SKILL and docs edits, and fanout.py did not change after it.
  - It passed again inside `check.sh` on the final tree.
- C2 (`! grep "Lane worktrees stay after the run"` in SKILL.md): exit 0.
- C3 (`grep "lanes.py sweep --apply"` in SKILL.md): exit 0.
- C4 (`grep "lanes.py open"` in SKILL.md): exit 0.
- C5 (the `allowed-tools` line names `scripts/lanes.py`): exit 0.
- C6 (`! grep "the worktrees stay for inspection"` in fanout.py and sdlc-internals.md): exit 0.
- C7 guard (`grep ".claude/worktrees/"` in SKILL.md): exit 0.
- C8 guard `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0.
- C9 guard `python3 scripts/check-packaging.py`: exit 0.
- C10 guard `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The fanout, lanes.py, run, hook, shellcheck and plugin validate selftests all passed.
- C11 guard `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: exit 0.
- C12 scope (only the 5 allowed files differ from base outside `.sdlc`): exit 0.

## Notes
- Settle will usually refuse in the real sub-agent flow:
  - Prep now writes a host record with `into: <integration>` for every solo ticket. Land rebinds it but leaves it open.
  - `lanes.evaluate` row 4 refuses to close an integration tree while any lane into that branch still has a tree or branch.
  - Land also queues the merged solo in prune.json, and sweep row 8 keeps a host lane for 6 hours after that.
  - So the new `## 5. Main` sequence (ff merge, then `fanout.py settle`) will usually print `lane still open: ... (lanes still open into <integration>: <host lanes>)` and exit 1 in the prep/land case. That lasts until T-0453's `dispatch.py prune --done` closes the host lanes.
  - The handoff lists row 4 as an expected refusal, so I built it as specified. The planner should know. Case 28 has no row 4 control.
- Settle behaves differently from T-0438 in two ways:
  - An integration branch with no worktree is now kept (`lane still open: <branch> (no worktree)`, exit 1). The old code deleted it.
  - The fast-forward still runs before the close, so main can move even when the close then refuses and keeps the branch.
- Roll removes the scratch tree unconditionally, as the handoff asks. If two rolls share one lanes dir at the same time, the first can remove the scratch the second already set up; I did not guard against that.
- The red checkpoint is `retrospective`, and 5 of the 6 `(red)` criteria were recorded. The cause is the same one the step-2 builder reported: steps 1 and 2 were already uncommitted in this lane when `record` ran.
- One SKILL.md edit is outside the handoff's list: sub-agent step 1 said prep "creates nothing". Prep now writes host records, so I changed it to name the dispatch and host records.
- `land_lanes` details:
  - It compares paths with `lanes.under` (realpath).
  - The rebound host record keeps the provisional record's `base_sha`.
  - An exception inside it never changes the land outcome or exit code.
  - Close lines print after the report. A successful full-lane close can include `ticket still open: <id>` lines, because the main tree's ticket is not done yet.
- The edit scripts lived under `.worktrees/tmp/0452-s3-builder-L3` and are removed. I created no worktree. The check.sh log went to a temp file under /tmp, which is now deleted.

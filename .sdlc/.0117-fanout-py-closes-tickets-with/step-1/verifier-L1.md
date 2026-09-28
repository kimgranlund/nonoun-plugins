<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `fanout.py run --help | grep -q -- --rewrite-refs`: pass. Evidence: exit 0 on the current tree. The same check against the HEAD version of fanout.py finds 0 matches, so it can fail.
- With the flag, the ticket closes and the rewrite lands in the `close` commit: pass. Evidence: I extracted the handoff's command and ran it, exit 0. It checks the report row `merged`, tip commit `close T-0001`, `docs/spec.md` holding the dot path and changed in that commit, `.sdlc/.0001-x/handoff.md` present, and a clean integration worktree.
- Without the flag, the close is refused, names the flag, and nothing is rewritten: pass. Evidence: the handoff command ran, exit 0. It checks rc 1, the report row `merged, close refused: .*--rewrite-refs`, status still `ready`, `docs/spec.md` unchanged, and a clean worktree.
- Dry-run plan with the flag: pass. Evidence: command ran, exit 0. It matches the `close: tickets.py close <slug> --rewrite-refs` line and checks that `.worktrees` was not created.
- Dry-run plan without the flag in numbered mode: pass. Evidence: command ran, exit 0. It matches the `close: tickets.py close <slug> (numbered folders` line.
- The selftest holds a numbered-mode case: pass. Evidence: the grep exits 0 on the current tree. HEAD's fanout.py has 0 matches for `ticket_folders: numbered`, so the check can fail.
- (guard) `fanout.py selftest`: pass. Evidence: exit 0, and check.sh's output includes "fanout selftest: PASS".
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py`: pass. Evidence: exit 0. `git diff --stat` for that file is empty.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. The output ends with shellcheck ok and plugin validate ok.

Checks on the builder's claims:
- I re-ran every acceptance command myself and did not rely on the builder's summary.
- The staging change is real. The diff replaces `git add -A -- <rel>` with a `porcelain()` snapshot before and after the close, staging `relp` plus the extra changed paths. It never runs `git add -A` over the whole worktree.

Steelman: I considered failing this step for not touching `skills/fanout/SKILL.md`, `CLAUDE.md`, and `sdlc-lite-author.md`. The handoff says all changes for this step are in `fanout.py`, and that criteria list has no docs check. The builder's note says those files belong to a later step, and `.sdlc/.../step-2/` exists. I dropped the finding.

## Out of scope changes
None in the source tree. `git diff --stat` shows `fanout.py` and `.sdlc/0117-fanout-py-closes-tickets-with/handoff.md`. The handoff.md change is planner or pipeline bookkeeping (12 lines) that this step did not touch. The other changes are untracked `.sdlc` artifacts (planner-L2.md, runs.jsonl, step-1/, step-2/).

## For the next attempt
None

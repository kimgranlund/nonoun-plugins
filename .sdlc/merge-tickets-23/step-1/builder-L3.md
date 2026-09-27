<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- Merge commit `0e5ce13` "Merge tickets-23: T-0119..T-0139 follow-ups" (parents f4585ad and the tickets-23 tip). Nothing was pushed.
- `plugins/sdlc-lite/scripts/run.sh`: both sides kept. From main: the result pick, `$pick`/`$last_ev`, and the Bash timeout floor (T-0105). From tickets-23: `detect_strays` and the `stray_worktrees`/`stray_branches` fields, now read from `$last_ev`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: every case from both sides kept, meaning the header comments, the base-sha cases, and the stray cases. The stray stub now emits compact JSON with `type:"result"` (`jq -nc`), because main's result pick only counts result events.
- `plugins/sdlc-lite/agents/planner.md`: rule 13 keeps main's `"$SDLC_BASE_SHA"` diff and adds tickets-23's clean whole-tree diff rule.
- `plugins/sdlc-lite/agents/verifier.md`: rule numbering follows main (rules 4 and 5, then 6 "only output"). Rule 3 adds tickets-23's "any add without `--detach`".
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: tickets-23's path-token wording kept, together with main's "its one follow-up ticket" (T-0142 cap).
- `CLAUDE.md`: merged word by word against the base. main keeps its timeouts, result pick, `SDLC_BASE_SHA`, Monitor, T-0142, and ancestry exception. tickets-23 adds the stray report, block-publish option words, the pattern-kill substitution, the detach and stray hook notes, the path-token rule, trailing-redirect lint, the whole-tree diff lint, fanout inherited-red after a driver rc, and dirty-before-sync.
- `.claude/agents/sdlc-lite-author.md`: 3-way word-level merge with no conflicts. Both sides' additions are present, T-0142 "Finish in session" included.
- `.sdlc/roadmap.md`: regenerated with `python3 plugins/sdlc-lite/scripts/tickets.py roadmap`.

## Checks
- Before the merge: `git status --short` showed only untracked `.sdlc/merge-tickets-23/`, so there were no uncommitted tracked changes.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: PASS. `shellcheck` on run.sh and run-selftest.sh: clean.
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: exit 0.
- `git merge-base --is-ancestor tickets-23 HEAD`: exit 0.
- (guard) `! git rev-parse -q --verify MERGE_HEAD`: exit 0.
- (guard) the conflict-marker `git diff-tree --cc HEAD` check: exit 0.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: exit 0, run both before and after the merge commit.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check`: exit 0, "ok: 147 tickets, roadmap current".

## Notes
- The plugin version was not bumped, per the handoff.
- In CLAUDE.md the word-level merge left one misaligned conflict in the run.sh bullet. I resolved it by hand: main's bullet with tickets-23's stray-report sentence inserted after "then runs `git worktree prune`.". A word diff of the final file against each side shows only the other side's intended changes.
- An earlier command accidentally created `/tmp/null` from a redirect typo. I deleted it right away.

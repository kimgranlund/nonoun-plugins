<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- Merge commit `ca69fc4` ("Merge tickets-20: T-0092..T-0118 follow-ups"). Parents are `5a7881e` (HEAD) and `d476465` (tickets-20). Nothing was pushed.
- `.claude/agents/sdlc-lite-author.md`: kept both sides. From tickets-20: archive/reference-scan text, the fail-fast `||` rule, no-verdict and inherited-red route details. From main: the porcelain lint and the swap route. The inherited-red line now says fanout makes no `<id>: <title>` lane commit and WIP-commits the tree like any other stop.
- `.sdlc/find-out-why-the-t/handoff.md`: kept main's evidence note in Context, plus tickets-20's `## Question` and `## Evidence` sections.
- `.sdlc/roadmap.md`: regenerated with `tickets.py roadmap`, not edited by hand.
- `CLAUDE.md`: started from tickets-20's steps.py and fanout.py entries, then added main's porcelain lint, the `swap` action and `steps.py swap` text, and the WIP-commit sentence. The inherited-red wording now says the work is kept in the stop's `wip(<id>)` commit.
- `plugins/sdlc-lite/agents/conductor.md`: tickets-20's verifier inherited red and "or a reverify", plus main's swap exception.
- `plugins/sdlc-lite/scripts/check.py`: both `PLAN_DEFECT_DOCS` entries kept (`clean porcelain status` and ``nonzero `exit` ``).
- `plugins/sdlc-lite/scripts/steps.py`: both docstring rules kept (bare `=` and porcelain), both `criteria_lines` and `COMPOUND_END`, and both selftest blocks. tickets-20's bare-assignment selftest block was relabelled `(k6)` → `(k7)` because both were `(k6)`.
- `plugins/sdlc-lite/scripts/fanout.py`: kept all of `wip_commit`, `porcelain` and `inherited_red`, and all selftest cases. Main's WIP case was renumbered 4 → 7. The docstring and the `inherited` comment were updated. The inherited-red selftest (case 5) now expects a clean lane tree and a `wip(T-0001): inherited red: step-1: test_a` tip that holds the step file and is not merged.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: main's `swap` action and item 8, plus tickets-20's verifier inherited red and "or a reverify" in the action list and item 7.

## Checks
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` (before commit): PASS.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` (before commit): PASS.
- `plugins/sdlc-lite/scripts/check.sh` before the commit: exit 0. After the commit: exit 0 (ends with shellcheck ok and plugin validate ok).
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: exit 0.
- `git merge-base --is-ancestor tickets-20 HEAD`: exit 0.
- (guard) `! git rev-parse -q --verify MERGE_HEAD`: exit 0.
- (guard) `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check`: `ok: 140 tickets, roadmap current`, exit 0.
- `git status --short` after the commit: empty.

## Notes
- The two batches disagreed on one behavior, and the verifier should confirm how I settled it:
  - Main (T-0126) WIP-commits every lane stop that is not `merged`.
  - The tickets-20 inherited-red outcome said "nothing is committed … tree left as is", and its selftest checked for an uncommitted file.
  - T-0126's written intent is "the lane tree is clean after any stop", for every outcome other than merged. So inherited red now gets a WIP commit too: the work is still kept, on the lane branch, and never merged.
  - That changed four things: one assertion in the tickets-20 fanout selftest, one sentence in the fanout.py docstring, one in CLAUDE.md, and one in the author agent. The /fanout skill text that merged on its own already matched.
- The plugin version was not bumped, as the handoff says.
- My scratch helper files under `$SDLC_TMP_WORKTREES` are deleted. No worktree was created.

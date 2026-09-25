## Task goal
Define `step-<n>.superseded-<k>/` as the name for a step dir replaced by a replan. `board.py` and `bench-summary.sh` skip it when counting steps, but still count its cost, and `/chain` and `handoff-format` document and perform the rename.

## Step 4: Audit the remaining step-* readers
level: L1
### Do
- Run `grep -rn 'step-' plugins/sdlc-lite --include='*.sh' --include='*.py' --include='*.md'`, excluding `bench/tasks` and `bench/results` fixtures.
- Confirm no unaddressed reader counts steps. Known remaining readers: `statusline.sh:46` (`step-[0-9]*` on a running-role path, which still names the step number), `board.py` `cost` and `has_step_work` (intentionally inclusive), and `tickets.py` (only fixture text).
- If the grep finds any other step counter in `bench.sh` or `skills/*`, make it skip superseded dirs.
- Update the `plugins/sdlc-lite/CLAUDE.md` Layout or board line if it describes step globbing. Also keep the `sdlc-lite-author` agent in sync only if it mentions step dirs.

### Acceptance criteria
- The grep output was reviewed and each hit is either a live-step-only reader, an intentionally inclusive reader, or a fixture. Report any change made.
- `plugins/sdlc-lite/scripts/check.sh` passes.

## Paths
Edit only files in this worktree (/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets7/plugins/sdlc-lite). Do not commit.

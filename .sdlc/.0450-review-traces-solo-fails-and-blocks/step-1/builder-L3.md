<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout37/m/docs/reports/2026-10-11-solo-fails-and-blocks.md (new): the report with the five required headings, 198 lines, 27 verifier and 11 builder evidence pointers, and `propose a ticket` used 3 times.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout37/m/.sdlc/0450-review-traces-solo-fails-and-blocks/sample.py (new): the sampler the verifier can rerun. It reuses `solo_stats.py` and `fleet_collect.py`. Defaults: the four repos, `--since 2026-10-08`, `--until 2026-10-11T20:00:00Z`, `--k 2`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout37/m/.sdlc/0450-review-traces-solo-fails-and-blocks/sample.txt (new): sample.py's output.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout37/m/.sdlc/0450-review-traces-solo-fails-and-blocks/scratch/ (new): stdout of each traces ingest, detect and clusters run and each fleet_collect run, plus the excerpts read for stages 2 to 4.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout37/m/.sdlc/0450-review-traces-solo-fails-and-blocks/step-1/red-checkpoint.jsonl (new, written by `redck.py record` before the first edit).

## Checks
- `redck.py record <handoff>` before the first edit: exit 0, 1 pre-edit control recorded red.
- `traces.py ingest`, `detect --repo` and `clusters --max 5 --repo` for each of the 4 repos: all exit 0. No `--rerun-criteria`.
- `fleet_collect.py collect <repo> --since 2026-10-08` for each of the 4 repos: all exit 0.
- `sample.py`: exit 0. Prints 166 solo tickets, 123 verified, 34 first-round non-passes (all 34 later passed or closed), 39 blocked notes in the window and 20 read.
- `sample.py --since 2000-01-01 --until none`: 174 blocked notes, 56 plan defect.
- Every criterion was run once with `SDLC_BASE_SHA=41cdd954...`:
  - (red) report count is 1: exit 0
  - headings: exit 0
  - pointers: exit 0 (27 verifier, 11 builder, all resolve)
  - `propose a ticket` cap: exit 0 (count 3)
  - T-ids: exit 0
  - K-005 and "89 of 123": exit 0
  - category words: exit 0
  - agents path: exit 0
  - trailing whitespace: exit 0
  - (guard) `docs_check.py`: exit 0
  - (guard) scope: exit 0
- After swapping ranked changes 1 and 2 so the order follows count, these were rerun: pointers exit 0, cap exit 0, trailing whitespace exit 0, `docs_check.py` exit 0.
- Em dash count in the report: 0. `git diff --check` on the report: clean.

## Notes
- The handoff says "K-005 has no file yet", but `docs/kpi/005-solo-first-pass-rate.md` exists in this tree because T-0449 landed. The report cites both that file and the baseline report.
- The handoff's 173 blocked notes (55 plan defect) are every note on disk with no date filter; that count is now 174 (56). Inside the window there are 39: maison 29, ultimate-tokens 8, agent-ui 2, which matches the per-repo numbers in the handoff's Context. The report states both counts.
- sample.py reproduces 166, 123 and 34 because of its default `--until 2026-10-11T20:00:00Z`. With `--until none` it prints 175 solo tickets and 128 verified, still with 34 non-passes.
- Stages 2 to 4 ran inside this builder, as the handoff asked; `## Unverified` says so. Each classification is one reader's judgment from the verifier files' fail lines and `## For the next attempt` sections.
- `skips.md` was already modified when this build started; this step did not change it. `sample.txt` and `scratch/` live in `.sdlc` as the handoff asks.

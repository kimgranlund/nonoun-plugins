<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/docs/reports/2026-10-12-compaction-prompt-replay.md: created; Method, Result table, "Run on this repository", "Live check", Follow-up.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/docs/reports/2026-10-12-compaction-prompt-replay/plan-doc-run.md: created; fixture, 17 turns, five probe questions.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/docs/reports/2026-10-12-compaction-prompt-replay/lane-wave.md: created; fixture, 18 turns, five probe questions.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/f/docs/reports/2026-10-12-compaction-prompt-replay/design-thread.md: created; fixture, 17 turns, five probe questions.
- Same folder, `plan-doc-run.prompt.txt`, `lane-wave.prompt.txt`, `design-thread.prompt.txt`: created; the prompt-arm blocks as first returned.
- Same folder, `<fixture>.summary-prompt.md` and `<fixture>.summary-free.md` for the three fixtures (six files): created; the two summaries per fixture.
- Same folder, `repo-run.prompt.txt`: created; the block of the run on this repository.

## Checks
All run from the tree root. `SDLC_BASE_SHA=07a5c289eae8ce19db8ed716c2400c10841d9ac2` was exported for the two base guards.
- Criterion 1 (report exists, T-0465, table header, "unverified: not an independent run"): exit 0.
- Criterion 2 (three fixtures with "## Probe questions", six table rows): exit 0.
- Criterion 3 ("## Run on this repository", `ok: compaction plan passes`, `lines: N of 60`, `Run: /compact`): exit 0.
- Criterion 4 ("## Live check", a line starting `unverified`): exit 0.
- After the last report edit, the greps of criteria 1, 3 and 4 were rerun together: exit 0. Criterion 2 was not rerun; the edit touched neither the table nor the fixtures.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 in 1542 s. It ran before the last report edit, a one-sentence change to the report.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: exit 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- (guard) `python3 scripts/check-packaging.py`: exit 0, PASS.
- (guard) `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`: exit 0, `PASS (293 checks)`.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs scripts .gitignore`: exit 0.
- (guard) scope diff against `$SDLC_BASE_SHA`: exit 0.
- Trailing whitespace in untracked files under `plugins` and `docs` (`grep -nE '[[:space:]]+$'`): no hits; the report was swept again after its last edit, no hits.
- `plan_check.py compaction` on first return, before any fix, all exit 0 with `ok: compaction plan passes`:
  - `plan-doc-run`: `lines: 21 of 60`, `pin: 10 of 40`.
  - `lane-wave`: `lines: 21 of 60`, `pin: 11 of 40`.
  - `design-thread`: `lines: 21 of 60`, `pin: 11 of 40`.
  - Run on this repository: `lines: 21 of 60`, `pin: 8 of 40`.

## Notes
- The replay table is not evidence that the prompt helps. I wrote the fixtures, the prompts, all six summaries and the scores; no summarizer model and no `/compact` ran. The free-arm summary is my estimate of what a bare compaction keeps, so the gap between the arms is an assumption of the method. The report says this in Method and marks the replay "unverified: not an independent run".
- Table totals: the prompt arm has 0 re-asked of 15, 0 rules violated of 6, 0 decisions lost of 9, and carries 336 words. The free arm has 6, 5 and 2, and carries 223 words. The before value of the ticket metric stays unmeasured until a live run.
- Do item 4 asked for `SDLC_HEADLESS=1`. I did not export it. The compaction kind asks no question and writes no file without `--write-handoff`, so no command of the run reads it; the report states this as it happened.
- The command list for the run on this repository ran for real (`compaction_handoff.py status`, `git status`, `gh pr list`, `dispatch.py status`, `steps.py next`, `report.py render`); the report lists each output.
- Live check line reads `unverified [U]`: a headless builder cannot run `/compact` and no live run is on record. `--write-handoff` stays off by default.
- `SDLC_BASE_SHA` was empty in the shell. The verifier must export `07a5c289eae8ce19db8ed716c2400c10841d9ac2` before the `git diff --check` guard and the scope guard.
- No criterion is tagged `(red)`, so `redck.py record` was not run.
- Nothing is committed; all work is in the tree. No throwaway worktree was created, and the `check.sh` log folder under the tmp prefix was removed.

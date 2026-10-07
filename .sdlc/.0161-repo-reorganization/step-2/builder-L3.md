<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `.sdlc/0161-repo-reorganization/handoff.md`: appended a `## Recommendation` section at the end of the file (39 added lines, no other lines changed). It contains:
  - the `Counts:` line and the 2-of-4 `ok` share
  - the N1, N2, N3, N5, N9 and N15 paragraphs
  - `### Rules to keep` and `### Rules to change`
  - `Apply verdict: defer` and its justification

  The front matter, `status:` and the earlier sections are unchanged.

## Checks
- `awk ... | grep -qE '^Apply verdict: (build|defer|drop)$'`: rc 0
- The loop over N1, N2, N3, N5, N9 and N15 `^$n:` in the Recommendation section: rc 0
- The loop over the `### Rules to keep` and `### Rules to change` exact lines: rc 0
- The python Counts check against `len(placed)`, `len(moves)` and `len(unplaced)` in `plan.json` (12, 4, 0): rc 0
- `awk ... | grep -qF 'plan.json'`: rc 0
- (guard) Front matter at `$SDLC_BASE_SHA` equals front matter now: rc 0
- (guard) `git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'` is empty: rc 0
- (guard) No untracked files outside `.sdlc/0161-repo-reorganization`: rc 0
- (guard) `git diff --check "$SDLC_BASE_SHA" -- .sdlc/0161-repo-reorganization`: rc 0
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check`: rc 0, "ok: 170 tickets, roadmap current"
- (guard) `python3 scripts/check-packaging.py`: rc 0, PASS
- `git diff "$SDLC_BASE_SHA" -- handoff.md` has no removed lines, only additions.

## Notes
- All gates were green, so step 1 left nothing to fix.
- Every claim cites `spike/plan.json`, `spike/plan.txt` or `spike/review.md` by line or key. The Rules bullets name sections and decisions of `docs/planning/repo-onboarding/reorganization.md` v0.6; that file was not edited.
- The recommendation is that the plan lives in a file outside `.sdlc/`, not in a ticket (N1, N9). The plan should be generated again and compared before use, so a hand-edited plan is refused (N15). Apply is deferred: once the two records are frozen, the plan is 2 moves and 13 line edits, which a person can apply by hand.
- The statement that `plan.json` has no `version` or `digest` field is based on reading its keys (lines 2-217).
- No em dashes in the added text.

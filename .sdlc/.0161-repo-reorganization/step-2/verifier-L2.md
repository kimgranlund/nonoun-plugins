<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `awk '/^## Recommendation/,0' .sdlc/0161-repo-reorganization/handoff.md | grep -qE '^Apply verdict: (build|defer|drop)$'`: pass. Evidence: rc 0, and the line reads `Apply verdict: defer`. On the base handoff the same pipeline matches 0 lines, so the check can go red.
- `for n in N1 N2 N3 N5 N9 N15; ... grep -q "^$n:"`: pass. Evidence: rc 0, and all six paragraphs start with their `N<n>:` label in the section.
- `for h in '### Rules to keep' '### Rules to change'; ... grep -qxF "$h"`: pass. Evidence: rc 0, and both headings appear as exact lines.
- Counts python check: pass. Evidence: rc 0. The line reads `Counts: placed 12, misplaced 4, unplaced 0`. A separate python pass over `plan.json` gave `len(placed)`=12, `len(moves)`=4, `len(unplaced)`=0. At base the `split('## Recommendation',1)[1]` step raises IndexError, so the check can go red.
- `awk ... | grep -qF 'plan.json'`: pass. Evidence: rc 0, and the section cites `plan.json` many times.
- (guard) Front matter equals the base front matter: pass. Evidence: rc 0. `git diff --stat` shows 39 insertions and 0 deletions, so `status: ready` is untouched.
- (guard) `git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'` is empty: pass. Evidence: rc 0. `git diff --name-only` lists only `.sdlc/0161-repo-reorganization/handoff.md`.
- (guard) No untracked files outside `.sdlc/0161-repo-reorganization`: pass. Evidence: rc 0.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- .sdlc/0161-repo-reorganization`: pass. Evidence: rc 0, no output.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check`: pass. Evidence: rc 0, "ok: 170 tickets, roadmap current".
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: rc 0, "PASS: catalog parity, identity, skill routes, hook isolation and context links".

I did not rerun the two gate criteria at the pre-build HEAD. They are green on the built tree, so an inherited-red comparison does not apply.

Builder claims I checked against the files:
- **Counts and ok share:** `plan.json` `summary` gives placed 12, misplaced 4, unplaced 0, and `review.md` lines 9-12 mark 2 of 4 moves `ok`.
- **N5:** `cite_forms` is markdown_link 12, backtick_path 6, in_frozen_files 25, and every other form 0.
- **N2:** `ambiguities` is `[]`, and `review.md` line 24 describes the probe runs.
- **N3:** `unplaced` is empty (`plan.json` line 179).
- **Rule names:** Decisions, Frozen material, Plan, Approve, Apply/Refusals and Open findings all exist in `docs/planning/repo-onboarding/reorganization.md` (rows at lines 16-19, headings at 35, 50, 77, 92). The rows the Keep/Change bullets name are in the Decisions table.
- **No em dashes:** `grep -c '—'` on the handoff returns 0.
- **Design doc untouched:** `git diff --name-only` lists no other file.

I drafted one fail reason and dropped it after checking. The N15 paragraph and its Change bullet do not name the design's `### Digest` rule (line 68). The design's own N15 finding says "the digest covers inputs only", so the recommendation's "no version or digest field" in `plan.json` and its regenerate-and-compare fix agree with it. The criteria do not require naming that heading, and the Change bullet does name the "Plan ... When the two disagree, `plan.json` decides" rule (line 66). This is a note, not a defect.

## Out of scope changes
None. The only tracked change is the appended `## Recommendation` in `handoff.md`. The other untracked files (`spike/`, `step-1/`, `step-2/`, `planner-L2.*`, `runs.jsonl`) are all under `.sdlc/0161-repo-reorganization/`.

## For the next attempt
None

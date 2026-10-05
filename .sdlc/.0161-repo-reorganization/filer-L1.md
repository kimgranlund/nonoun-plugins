<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0161: Spike: read-only reorganization plan on this repository

## PR body
### Summary
T-0161 is a spike. It tests the rules in `docs/repo-onboarding/reorganization.md` (v0.6) against this repository's real files. It also asks which open findings (N1, N2, N3, N5, N9, N15) show up in practice.

The recommendation is written into `.sdlc/0161-repo-reorganization/handoff.md`. Its apply verdict is **defer**. A reviewed plan that a person carries out by hand is enough for this repository.

The changes are all under `.sdlc/0161-repo-reorganization/`. The prototype moves and rewrites nothing, and it creates no ticket.

### Changes
- `spike/layout.md`: trial layout with the homes `maintenance/`, `reference/` and `reports/`. It freezes `docs/reports/`, `docs/reports/readiness-recovery-validation.md`, `plugins/sdlc-lite/bench/results/` and `plugins/sdlc-lite/adapters/codex/agents/`. `generative-constructs` and `repo-onboarding` stay topics.
- `spike/reorg_plan.py`: throwaway read-only planner. It uses the standard library and imports the T-0160 parser from `onboard.py`.
- `spike/plan.json` and `spike/plan.txt`: output of the run on base `9d6ca64`.
- `spike/review.md`: a person's ok/wrong verdict on each move.
- `handoff.md`: appended a `## Recommendation` section (39 added lines, front matter unchanged).

### Findings
- Counts: placed 12, misplaced 4, unplaced 0. The review judged 2 of the 4 moves `ok`. It marked `docs/claude-handoff.md` and `docs/claude-response.md` `wrong`, because both are dated correspondence that a person would freeze.
- N1: it occurred. Planning again after a fix is the normal path, so the plan should live in a file outside `.sdlc/` that each run overwrites, not in a ticket.
- N2: none of the ambiguous inputs occurred. Detection works on probe layouts (`multi_home`, `into_frozen`, a case-folded `name_collision`). The two-sources-one-destination case was not exercised.
- N3: no topic glob was needed.
- N5: it occurred. Of the cites of moved documents outside frozen files, 12 are Markdown links and 6 are backticked paths. None of the 6 should be rewritten.
- N9: it would occur if the plan were a ticket.
- N15: real as designed. `plan.json` has no version or digest field, so a consumer should generate the plan again and refuse on any difference.
- Rules to keep and rules to change are listed in the recommendation with line-cited evidence. The main change is to widen the frozen-candidate test to `Date:` lines. It missed both records.

### How each was verified
- Step 1 (prototype, builder L3, verifier L2: pass):
  - A fresh `--json` run matches `plan.json` with no diff.
  - The four required paths are frozen; a negative control that freezes only `docs/reports/` fails the assertion.
  - Both generative-constructs links are in `baseline_broken`.
  - No frozen path appears in the moves or rewrites.
  - The script only reads: the only `open` is `'rb'`.
  - The verifier's own `git grep` of the four moved files confirms the 12-link count.
  - Probe runs triggered `multi_home`, `into_frozen` and a case-folded `name_collision`.
- Step 2 (recommendation, builder L3, verifier L2: pass):
  - The apply verdict line is present.
  - The N1, N2, N3, N5, N9 and N15 paragraphs and both Rules headings are present.
  - The Counts line matches `len(placed)`, `len(moves)` and `len(unplaced)` in `plan.json`. The check fails at base.
  - The front matter equals its base.
  - The diff has only additions.
  - `git diff --check` is clean.
  - `tickets.py check` gives "ok: 170 tickets, roadmap current".
  - `scripts/check-packaging.py` passes.
- Guards for both steps: no tracked change outside `.sdlc/` against the base SHA, and no untracked file outside `.sdlc/0161-repo-reorganization/`.

### Limitations
- The two-sources-one-destination collision path was not exercised. No two documents under `docs/` share a file name.
- The verifier noted, as a note only, that the N15 paragraph does not name the design's `### Digest` rule.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
None for the product. This is a spike and ships no production code. The recommendation is recorded in `.sdlc/0161-repo-reorganization/handoff.md`.

## Follow-ups
- decide: Whether to build apply for the reorganization or drop it. The spike recommends deferring, since a reviewed plan is 2 moves and 13 line edits by hand. Revisit only when a repository's plan is too large to carry out by hand.
- decide: Whether to update `docs/repo-onboarding/reorganization.md` to v0.7 with the "Rules to change" list (plan file outside `.sdlc/`, the `Date:` frozen-candidate test, the added plan fields, regenerate and compare for N15).
- fix-now: Freeze `docs/claude-handoff.md` and `docs/claude-response.md` in a real `docs/layout.md` before any reorganization of this repository uses the plan.
- note: The two-sources-one-destination collision code path in `reorg_plan.py` was never exercised on this tree.
- note: A broad glob such as `claude-*.md` pulls the placed file `docs/maintenance/claude-hooks.md`, so the design's glob rules need a warning for it.

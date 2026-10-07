<!-- role=architect level=L1 model=fable effort=high -->
## Approach

The handoff is a review brief, not a build brief: fact-check `docs/specs/generative-constructs/progressive-context-gap-analysis.md` (150 lines, HEAD 61404dd) against its own citations. The design question is how to make that review independent and reproducible rather than a second reading of the same prose. The outside-in plane groups the analysis by source family (Progressive Context skill files, the proposal set, validation and `.sdlc` records, SDLC Lite code and onboarding docs, `docs/planning/docs-schema/design.md`, outside-repo sources), plus the label audit, the score arithmetic, the cross-check list, the ranked list, repository-state claims, format, and the review record. The inside-out plane was taken from the handoff's six numbered checks, not from the analysis's headings, plus two it implies: claims about repository state (tickets filed, files present, links resolving) and the shifted README line numbers. The manifest crosses clean in strict plan mode (14 nodes, 16 actions, 26 hosts, 13 edges).

I ran the review itself as the verification of the design's load-bearing assumptions, since every finding depends on what the sources actually say. Every `path:line` in the analysis was opened with `sed -n`; the count is about 60 distinct citations in 94 backticked path strings. The result is written to `.sdlc/0247-pc-gap-analysis/review/decompose/report.md` in the handoff's shape (Verdict, Findings, Missed gaps). Verdict: fail, on three factual errors that mislead, each a small edit: the tier arithmetic (eleven tiers scored, 16 of 33, not "ten" and "of 30"; the 36-point scaling is derived from the wrong max against a rubric with 13 `## T` headings), the "tickets filed" sentence (no ticket above 0247 exists), and cross-check item (c) plus R1's rationale, which ask to build a drift check that `onboard.py check` already performs for `docs/AGENTS.md`. Eleven minor findings cover citation precision (README lines shifted by two by the analysis's own commit 881808d, a wrong line range in `04-context-and-harness.md`, a commit subject cited where `design.md:104` says it directly), labels ([E] defined and never used; the rubric at an absolute path outside the repo is labeled [O]), and overstatements ("some runs" from one run's limit). Scores, the tier map, and the what-not-to-build list otherwise hold against the cited material.

The remaining work is one builder step on the analysis file applying the fixes in report.md, then the review record the ticket's Done condition names, which this report already is (the README's line-7 link points at `docs/reports/progressive-context-gap-analysis-review.md`, which does not exist yet; either materialize it from this record or repoint the link).

## Interfaces

- New: `.sdlc/0247-pc-gap-analysis/review/decompose/manifest-v1.json` (domain goals, plan mode, strict clean).
- New: `.sdlc/0247-pc-gap-analysis/review/decompose/report.md` (decompose header, then `## Verdict`, `## Findings` 1-14 with blocker/minor and a fix each, `## Missed gaps`).
- Unchanged: `.sdlc/0247-pc-gap-analysis/review/handoff.md` (frozen, `.run.lock` present; the `Decomposition:` line was not added).
- To change (next step, not by me): `docs/specs/generative-constructs/progressive-context-gap-analysis.md` lines 9, 10, 27, 31, 40, 42, 56, 58, 68, 72, 89, 113, 115, 123, 125, 134, 150; `docs/specs/generative-constructs/README.md:7` link target.

## Constraints and assumptions

- The handoff's output shape is Verdict/Findings/Missed gaps while this role's message format is fixed: verified by reading both; the review substance lives in report.md and this message carries the design and the blockers.
- `onboard.py check` already renders `docs/AGENTS.md` from `docs/layout.md` and labels a hash mismatch `stale`: verified at `plugins/sdlc-lite/scripts/onboard.py:221-226,369,451-465,581,696-711,1140-1152`; `tickets.py:145,189` imports those helpers for the `.sdlc` router.
- The rubric has 13 `## T` headings and a band topping at 36: verified by `grep -c "^## T"` (13) and lines 99-104 of `/Users/kimgranlund/.claude/skills/generative-systems/references/review-rubric.md`.
- The analysis table scores eleven tiers summing to 16: verified by counting rows at analysis lines 35-40.
- No ticket above 0247 exists: verified by `ls .sdlc/024[8-9]* .sdlc/025*` (no match).
- `design.md` at HEAD is the 5a1165e version the analysis names: verified by `git log --oneline -- docs/planning/docs-schema/design.md` (last change 5a1165e).
- README line shift is caused by the analysis's own commit: verified by `git show 881808d^:docs/generative-constructs/README.md | sed -n '21p;45p'` showing the cited sentences at the old numbers.
- `docs/layout.md` is absent here: verified by `ls` and `onboard.py:317,699-711` (written on setup).
- "Codex rollout absent" is one run, not some: verified by `grep -il rollout docs/reports/*.md` (ten files, one absence statement at `codex-conductor-solo-live-run.md:23`).
- Maison mentions "progressive context" only as a gen-ui concept: verified by `git grep -i "progressive context"` in `/Users/kimgranlund/Projects/maison/ui-kit-maison` (three files, all gen-ui).
- The placement proof is absent from design.md v0.2: verified by `grep -i 'fresh session\|hidden-answer'` (empty); line 183 is the migration inventory.
- `check-packaging.py` checks links in plugin context files: verified at `scripts/check-packaging.py:59,75`.
- Whether the rubric's 36-point band intends to exclude one tier: unverified (the rubric does not say).

## Rejected alternatives

- Editing `review/handoff.md` to add the `Decomposition:` line: the handoff is frozen (`.run.lock`, attempt record binds its sha256); report.md notes the omission instead.
- Running the fact-check as a separate builder or verifier step after this design: every design decision here depends on what the sources say, and the ticket asks for one independent review; a second pass would re-read the same 60 citations for no new information.
- Deriving the inside-out plane from the analysis's section headings: that reads one plane off the other and would have missed the repository-state claims (tickets filed, `docs/layout.md`) that produced a blocker.
- Pass with notes: the handoff's rule is fail only for factual errors that mislead; the "ten tiers, 16 of 30, 19 of 36" line, the "tickets filed" sentence, and a recommendation to build an existing check each mislead a reader, so pass would misreport.
- Treating the rubric's 13-versus-12 tier inconsistency as the analysis's error: it is the rubric's; the finding asks the analysis to name it and give the scalings, not to resolve it.

## Risks

- The tickets for R3, R4, R6, R7, R8 may be filed in another session before the doc merges; then blocker 2 becomes a wording fix only. The verdict should be re-read against `.sdlc/` at merge time.
- A revision of `docs/planning/docs-schema/design.md` is in review elsewhere (analysis line 110); if it lands first, cross-check items (b) to (e) and finding 3's "until build ticket 1" clause need re-checking against the new lines.
- The rubric file is user-scoped and changed today (mtime Oct 5 05:26); a later edit to its tier headings or bands would move the arithmetic in finding 1.
- If the conductor expects the review output in `architect-L1.md` itself rather than in report.md, the verdict is only in Carry forward below and the findings must be read from report.md.

## Carry forward

- Verdict: fail, three blockers, eleven minor; full text at `.sdlc/0247-pc-gap-analysis/review/decompose/report.md`.
- Manifest: `.sdlc/0247-pc-gap-analysis/review/decompose/manifest-v1.json`, `coverage_check.py --strict` exit 0.
- Blocker 1: analysis lines 40,42 say ten tiers, 16 of 30, 19 of 36; table has eleven tiers = 16 of 33; rubric has 13 `## T` headings, band to 36 (rubric:99-104).
- Blocker 2: analysis line 134 "Tickets filed" is false at HEAD 61404dd; `ls .sdlc/024[8-9]* .sdlc/025*` matches nothing.
- Blocker 3: analysis lines 115,123 ask for a docs/AGENTS.md drift check that exists: `onboard.py:581` labels `stale`, render at `:696-711`, layout feeds model at `:451-465`.
- Real remaining gap behind blocker 3: `## Kinds` and `## Legacy` are not in the rendered model until build ticket 1 (`docs/planning/docs-schema/design.md:151`).
- README citations shift by +2 (45 to 47, 21 to 23, 7-14 to 9-16); cause is commit 881808d, confirmed via `git show 881808d^:docs/generative-constructs/README.md`.
- `docs/specs/generative-constructs/README.md:7` links to `docs/reports/progressive-context-gap-analysis-review.md`, which does not exist.
- `docs/layout.md` does not exist in this repo; `onboard.py setup` writes it (`onboard.py:317`).
- Analysis defines [E] (line 5) and never uses it; rubric and W3C PROV are labeled [O].
- Citation inventory: `grep -o '`[^`]*\.\(md\|json\|sh\|py\)[^`]*`'` over the analysis file, 94 strings, about 60 distinct.
- Maison hits for "progressive context": `git grep -i` in `/Users/kimgranlund/Projects/maison/ui-kit-maison`, 3 files, all gen-ui.
- `review/handoff.md` is frozen (`.run.lock`); no `Decomposition:` line was added.
- Both written files have 0 em dashes (`grep -c $'\u2014'`).

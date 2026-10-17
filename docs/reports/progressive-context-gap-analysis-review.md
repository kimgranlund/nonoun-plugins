# Progressive Context gap analysis review

Recorded: 2026-10-05. Ticket T-0247. Reviewed: `docs/specs/generative-constructs/progressive-context-gap-analysis.md` at commit 61404dd (150 lines). Reviewer: `run.sh architect L1` (Fable high), a different model family from the author (Sonnet). Raw record: [`.sdlc/.0247-pc-gap-analysis/review/decompose/report.md`](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0247-pc-gap-analysis/review/decompose/report.md).

## Verdict

Fail on first pass: three factual errors that mislead, eleven minor findings (about 60 distinct citations opened; the rest resolved and supported the claims). All three blockers and the minor findings were applied in the next commit. The fixed text was not re-reviewed; the architect is the only independent check.

## Blockers and how each was applied

| Finding | Applied |
| --- | --- |
| Tier arithmetic: eleven tiers scored, 16 of 33, not "ten" and "of 30"; the rubric has 13 tier headings but bands to 36 | Total corrected; the rubric inconsistency is named and the 13 to 24 band shown to hold under each reading |
| "Tickets filed" was false at review time | Tickets T-0252 to T-0256 filed, and the sentence names them |
| Cross-check item (c) and R1 asked to build a drift check that `onboard.py check` already performs for `docs/AGENTS.md` (`onboard.py:221-226,451-465,581,696-711`) | Rewritten: the check exists for homes; the real gap is that `## Kinds` and `## Legacy` are not in the rendered model |

## Minor findings applied

README line numbers shifted by the analysis's own link commit; wrong line range for the browser-harness proposal; `docs/layout.md` described as a file `onboard.py setup` writes; one run, not "some runs", lacked a Codex rollout; the 60-line target cited from `design.md:104` and `onboard.py:321`; inference labels added; [E] used for the rubric and W3C PROV; example path corrected; maison hits listed; scope of the scores stated; the packaging link check named.

## Missed gaps the reviewer raised

A citation resolver (added to R6, T-0254); R4's home is `onboard.py check` (T-0253); the gap-analysis review link in the README needed this file (now present).

## Limits

One reviewer, one pass. The reviewer could not confirm whether the rubric's 36-point band intentionally leaves out a tier. A revision of `docs/planning/docs-schema/design.md` in review elsewhere may change cross-check items (b) to (e).

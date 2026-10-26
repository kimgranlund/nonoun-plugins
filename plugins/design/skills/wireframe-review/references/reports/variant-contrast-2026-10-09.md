# Variant contrast instruction comparison

Promoted the tested SKILL entry and intent-contract alternative guidance after an 18-generation development comparison and six-generation unseen holdout. Runtime assets, tokens and component conventions were identical between conditions. Only two guidance files differed. No first-pass artifact was repaired after freezing.

## Results

Scores are pooled medians of two condition-masked model reviewers across three repetitions per condition. Contrast is the weakest of A/B, A/C and B/C on a 0-4 scale. Quality and family use 1-5 scales.

| Brief | Baseline contrast | Candidate contrast | Baseline quality | Candidate quality | Family, both |
| --- | --- | --- | --- | --- | --- |
| Settings | 1 | 3 | 4 | 4.5 | 5 |
| Evidence | 2 | 3 | 4 | 4.5 | 5 |
| Booking | 1 | 3 | 4 | 4 | 5 |
| Unseen batch queue | 1 | 2 | 3.5 | 4 | 5 |

Each brief passed its frozen comparative gate: improved median weakest-pair contrast, no lower median quality or family, no increase in required-capability or critical failures, and complete candidate requirement coverage. Candidate holdout contrast scores span 2-3, so improvement does not mean every pair delivers two consequential structural differences.

Both reviewers independently produced the same per-brief development median contrast results. Holdout candidate medians were 3 and 2; both baseline medians were 1. Preserve this disagreement rather than treating the pooled result as unanimity about strength. Both reviewers correctly rejected cosmetic-only and capability-incomplete controls.

Root rendered 24 artifacts across A/B/C, desktop/mobile and light/dark: 288 startup combinations, no captured page errors. These checks establish bounded renderability; screenshots are scriptless visual snapshots. Independent task verification used actual live controls and resulting state, including save/reset/validation, evidence selection/runner-up, booking constraints, and batch block/retry/apply/undo.

## Observed defects and evaluation learning

One baseline holdout (queue-1-baseline) leaves all five rows visible under either status filter. Draft all-visible selects only three records despite five visible rows. Both reviewers confirmed it after a targeted recheck; the original disagreement is retained. Hidden-selection persistence stays untested for that output because rows never hide. Frozen artifacts retain the bug.

The first reviewer caught the filter defect; the second initially passed the requirement by observing selected IDs rather than verifying excluded rows disappear. Filtering checks must compare visible record identities with the filter and selection result. This is a verification lesson, not evidence that all baseline outputs have the defect.

Contrast improved through independent task hypotheses and experienced transitions. Merely shifting panels or changing the verbal rationale still produced weak pairs. Keep a shared style foundation, preserve task capabilities, and evaluate the weakest pair separately from task fitness. Avoid prescribing a fixed trio such as form/wizard/dashboard for every brief.

## Limits

These are small-sample model reviews, not human usability findings or broad reliability certification. Development rationale blinding was imperfect: one reviewer incidentally saw a rationale for one specimen; the other saw shell rationales before structural notes. Condition identities remained hidden. Fresh holdout reviewers recorded inner-screenshot judgments before source or rationale inspection.

Complete keyboard operation, assistive technology, measured contrast, Safari and systematic narrow-screen task completion remain unverified. Some generator standard behavior gates were unverified without adapters; separate evaluator task evidence does not retroactively turn those gates green. Model/settings were inherited consistently, but exact model/version, sampling and token telemetry were unavailable. Do not infer production performance or accessibility from these scores.

## Evidence

[Machine-readable scores, disagreements and limits](variant-contrast-2026-10-09.json) preserve per-run reviewer scores. Raw frozen corpora, briefs, protocol, first-pass outputs, screenshots and interaction logs remain in the experiment directory recorded there. Development and holdout hashes were rechecked before promotion. The unseen task was authored only after the development gate passed; neither candidate guidance nor thresholds were tuned on its results.

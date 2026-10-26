# Split-consumption follow-up: bounded peer specification

Date: 2026-10-11. Status: ready for peer planning/execution when authorized. This document scopes proposed work; writing or receiving it does not grant additional filesystem privileges or authorize unrelated changes.

## Objective

Resolve the confirmed routing and verification-reporting failures, qualify an enforced author/evaluator access boundary, then obtain one uncontaminated revision observation. Separately test that skill-report-card preserves the evidence qualifications. Do not repeat the successful standalone/review author trials or turn this into a full-system reliability study.

Primary evidence:
`/Users/kimgranlund/.codex/skill-previews/wireframe-review/planning/evidence/split-consumption-confirmation-2026-10-11-1/evaluator/report.md`

Read that report first. Read only the affected evidence files it cites as needed; do not load the entire evidence directory into a conversation. Keep the original report, submissions, weak evaluator, corrected evaluator, fault copies and telemetry immutable.

## Established findings and uncertainty

- Standalone and review operations passed the stated Chromium 390/1280 light/dark cases. Reuse these results within their exact scope.
- Revision behavior passed observed cases, but the author executed/read evaluator/revision-check.mjs. That attempt cannot establish clean-context efficacy. Retain it as contaminated evidence, not a failed behavioral run or a valid clean-context success.
- Review/revision required markers sit separately under flex-column labels rather than inside the maintained inline label wrapper.
- Custom geometry/layout and nested containers require source/visual diagnosis. Five unknown-style-owner warnings are not themselves five confirmed defects. Fixed-height preview captures do not certify complete vertical flow.
- Standalone CHECKS.md claimed Playwright unavailable despite a recorded successful resolver launch. No standalone author interaction check was recorded; evaluator interaction checks are separate.
- Read-containing command returns were 72,320 / 295,410 / 1,387,892 bytes. These include mixed commands, are not model tokens, and are not comparable efficiency rankings. Do not invent an overhead improvement target from them.

## Ownership and source authority

| Area | Authority / entry | Ownership boundary |
| --- | --- | --- |
| UI source/recipes | `/Users/kimgranlund/.codex/skills/base-ui/assets/recipes/reservation.html`, `reservation.js`, `review-field-label.html`; applicable component contracts | Edit base-ui source, not generated review copies |
| UI context route | base-ui `references/style/components/authoring.md`, `scripts/component-context.mjs` | Retrieve only applicable records; preserve bounded reads |
| Review authoring route | wireframe-review `references/workflows/build-core.md`, `scripts/demonstration-context.mjs`, applicable runtime contract | Register with the review adapter; do not replace the host |
| Browser availability | base-ui `scripts/resolve-browser.mjs` and its recorded result | Resolution/launch evidence is distinct from user-activation evidence |
| Evaluation machinery | Cited evaluator scripts/protocol; new version under fresh `/private/tmp` | Copy and version; never alter the original evidence |
| Report qualification | skill-report-card `scripts/adapters.py`, current adapter tests and handoff | Coordinate with its active owner; do not overwrite ongoing adapter work |
| Methodology | generative-systems `references/rapid-experiments.md`, `verification-and-drift.md` | Update only supported reusable lessons, not this task's entire history |

At start, inspect current source identities and existing handoffs for equivalent completed/active work. Reuse qualified fixes. Record exact file ownership before editing. Do not edit peer-owned live `sheets/components.html` or publish another preview destination. This scope does not require an ultimate-tokens repository change.

## Work items

### W1. Enforce the author/evaluator boundary before any author call

Prepare a new evaluation runner configuration that exposes only the fresh skill pair, the task prompt, a sealed uncontaminated predecessor and a writable author output directory. Evaluator code/results, grading rubrics, original study reports and other submissions must be outside the author's accessible surfaces.

A pathname convention, a prompt exclusion or chmod under the same full-access user is insufficient. Use an available enforced sandbox/container/separate execution identity, including restrictions on host tools that could read outside it. Do not seek privileged setup implicitly. Record the exact enforcement mechanism and its limitations.

Preflight from the SAME identity and tools available to the author:

- Positive: read approved skill material and predecessor; create only the allowed output.
- Negative: reading and executing evaluator code fail; reading a harmless canary outside the allowlist fails; symlink/path traversal and a child-process read do not bypass the boundary. Never use a real secret/holdout as a canary.
- Negative: changing the predecessor is rejected or reliably detected and fails submission. Distinguish filesystem prevention from post-run preservation detection.
- Ensure error responses do not disclose evaluator contents. Record tool configuration, not only an isolated shell test if the author also has broader tools.

If enforcement cannot be demonstrated, stop before author dispatch. Deliver the boundary findings and corpus fixes; mark confirmation unrun. A later behavior probe may be useful only if explicitly labelled non-clean and separately authorized.

### W2. Repair the smallest authoring/context seam

Inspect the maintained reservation recipe and required-label composition first. Determine why the review author did not consume them. Upsert the bounded route so matching reservation tasks retrieve one authoritative baseline and only needed family/runtime records. Do not add the entire catalog or evaluation material to SKILL.md.

Correct confirmed required-label and composed-geometry issues in their owning recipe/contract when needed. If maintained recipes are already correct, change routing/examples rather than patching frozen generated evidence. Document each custom radius/inset/grid finding as confirmed defect, supported customization or unverified; do not blanket-ban local layouts. Preserve page gutters, selected states, error relationships and variant state isolation.

Affected checks:

- Maintained label text and required marker remain inline and wrap together at narrow width.
- Local control/card geometry resolves from intended context roles; inspect actual computed geometry, not only class names.
- Full leaf flow remains reachable/scrollable; distinguish iframe clipping from leaf overflow.
- Copy-only negative control restores the separated required marker and is detected by a positional/structure check.
- An intentionally detached/incorrect geometry binding fails the relevant source/computed assertion; do not assert arbitrary fixed pixel values for all contexts.
- Reuse `scripts/check-reservation.mjs` where its assertions match the changed behavior. Do not run unrelated component matrices.

### W3. Separate availability, checks and claims

Update the relevant reporting instructions/template to record these independently:

1. dependency resolution;
2. browser launch;
3. author-performed activation checks (case, artifact and result);
4. independent evaluator checks;
5. untested conditions and delivery mode.

A successful resolver record must not be summarized as unavailable. Successful launch alone must not become an interaction pass. If a later launch fails, retain both timestamped/environment-bound facts rather than overwriting the earlier result.

Positive check: successful launch + no author interaction evidence yields “available; author activation unverified.” Negative controls: contradictory unavailable summary, fabricated author check from evaluator results, and launch-only result presented as task acceptance are rejected/flagged. Do not rewrite the historical CHECKS.md.

### W4. Freeze and run one revision confirmation

Only after W1 passes and W2/W3 affected checks pass:

- Freeze a fresh source/dependency snapshot. Record exact hashes, protocol, model and effort before dispatch.
- Use gpt-6-luna / low to retain the previous probe's settings if available. If unavailable, record the changed setting before dispatch and do not imply direct comparability.
- Use the uncontaminated REVIEW predecessor from the cited batch, not the contaminated revision. Check its sealed hash set and IDs against original preservation records. Copy it into the author boundary.
- Give the author the same revision requirements: maximum two items; no silent replacement; conditional lighting note with associated error/focus; note retained across toggle/save/restore; existing operations, variants and review identities preserved. Do not reveal evaluator internals or diagnostics.
- Budget: one author attempt, maximum 15 minutes, zero post-submission author repairs, no automatic replacement attempt. Ordinary self-checking is allowed before first declared submission; retain its full trace.
- Seal source/controller/output immediately at submission; record timeout/invalid output in the denominator. Never patch the submission in the evaluator.

Reuse the corrected evaluator machinery. It must select the page composition before A/B; locate the generated page/leaf structure rather than assuming exactly two frames. Keep the declared note-specific error target/message predicate. Qualify the retained cap and swapped-error faults against evaluator-only copies before scoring.

Check both alternatives at 390/1280, light/dark in Chromium: prior reservation operations; two-item cap; unresolved-error retention; conditional note association/focus; typed-note preservation; save/edit/restore; state isolation; review/export identity; predecessor hash preservation. No broader browser/AT certification.

Permit one bounded evaluator correction if a harness defect is demonstrated. Preserve its original result and rerun affected checks equally on the same sealed positive/fault copies. No new author attempt. Stop if the evaluator remains invalid or author access is contaminated; report unresolved.

### W5. Qualify the report-card interpretation separately

Coordinate this item with the active skill-report-card owner. Read its current handoff before changing adapters; acceptance-identity work may already be active. The narrative report alone is not sufficient to calculate a KPI. Use bounded structured source selections and hashes.

Add fixture/adapter controls that preserve these separate dimensions:

| Source fact | Required representation | Rejection control |
| --- | --- | --- |
| Evaluator behavior passes | Reported scoped behavior with criterion/environment provenance | Cannot become full-system acceptance |
| Revision evaluator access | Contaminated clean-context eligibility; observed behavior retained | Must not enter clean-context success denominator |
| Draft generation | Draft gates with incomplete delivery acceptance | Draft pass cannot become complete delivery |
| Unknown style owner | Unverified observation pending diagnosis | Must not automatically increment confirmed-defect count |
| Byte telemetry | Read-containing command-return bytes plus classifier limits | Cannot be relabelled tokens or cross-task efficiency improvement |
| Preservation | Original/artifact hash checks | Cannot substitute for behavior success |

Keep all KPIs unmeasured where attempt identity, source applicability or denominators are unqualified. This batch does not authorize general aggregation, target changes or a user-system scan. Report-card fixtures must not launch another author study. Process raw evidence outside the caller conversation; return compact normalized findings only.

## Deliverables and evidence matrix

Create a fresh disposable work directory under `/private/tmp`; retain final evidence within the owning skill's existing resources/reports location. Do not create sibling public preview sites. Preserve before/after identities and all failed attempts. Do not inspect or expose the sealed holdout.

Return:

1. A concise handoff with changed files, ownership, root causes and unresolved findings.
2. `criterion-evidence-matrix.json`: criterion ID, authority, source change, context change, positive evidence selection/hash, negative-control selection/hash, outcome, applicability/limitations. Use explicit unrun/not-applicable states.
3. Boundary preflight configuration/results, finalized protocol, snapshot manifest, sealed submission identities and scoped observations if W4 ran.
4. Telemetry with separate successful tool returns, repeated source reads, generated-artifact inspection and evaluator access. Preserve the old classifier separately. No ranking from dissimilar tasks.
5. Publication status: installed-source reconciliation, affected checks and package parity when publication is separately authorized. Do not silently publish generated author candidates or overwrite canonical/peer HTML. “Not published” is a valid explicit status.
6. At most five remaining actions, ordered by evidence and dependency.

Suggested criterion IDs: ISO-01 approved access, ISO-02 evaluator denial, ISO-03 alternate-tool denial, UI-01 required labels, UI-02 geometry diagnosis, UI-03 vertical reachability, REP-01 truthful check provenance, REV-01 prior behavior, REV-02 cap, REV-03 conditional note, REV-04 preservation, CARD-01 contamination, CARD-02 delivery mode, CARD-03 telemetry qualifiers.

## Stop rules and claims

No equivalent completed work is rerun merely to populate a new report. No author trial before isolation qualification. No second trial after contamination/timeout. No widening to a model sweep, full browser matrix, new KPI system or compatibility retirement. Do not migrate or retire legacy files in this batch.

Conclude separately: corpus fix status; enforced-boundary status; observed revision behavior; clean-context eligibility; report-card interpretation. One eligible passing revision supports only this scoped confirmation. It does not establish general reliability or causal improvement against a matched baseline.

## Paste-ready peer request

Read `/Users/kimgranlund/.codex/skills/generative-systems/resources/split-consumption-followup-peer-spec.md`. Check current ownership and equivalent completed work first. Implement the bounded authoring/reporting fixes and qualify the author/evaluator access boundary before spending the single revision attempt. Coordinate W5 with the report-card owner rather than overwriting its active adapter work. Preserve original evidence, accepted limitations, sealed holdout and peer-owned files. Return the criterion-to-evidence matrix, publication status and remaining issues. If enforced isolation is unavailable, do not run a trial labelled clean-context.

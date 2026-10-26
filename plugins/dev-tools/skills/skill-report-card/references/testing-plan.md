# Testing plan

## Execution layers

A. Deterministic unit/integration fixtures via `python3 scripts/test_scan.py`. No user-wide scan or model calls. Current automated coverage is listed in the test output; this plan is broader than the implemented suite.
B. Browser smoke on the generated fixture dashboard: open file URL, inspect all skills/filter, keyboard disclosure, 390/1280 widths, light/dark, safe rendering and no-script fallback. Use the installed browser resolver rather than hardcoded runtime paths. Record exact environment; no native Safari/AT claim from headless tests.
C. Bounded local discovery pilot only after user requests a real report: cap reads, inspect compact summary, review coverage in artifact, and compare a manually curated fixture subset. No raw evidence into parent context.
D. Adapter fixtures, then matched frozen reports, then optional semantic evaluator. Do not spend author/evaluator calls on unqualified mechanics.

## Discriminating matrix

| Area | Positive | Negative / expected limitation |
| --- | --- | --- |
| Root discovery | Matching report under a selected project/skill tree | Missing root recorded; budget leaves later roots unvisited |
| Exclusions | Ordinary project files reachable | Secrets, chat/session store, .claude private tree, sealed holdout and explicit excluded root never read |
| Filesystem | Regular small JSON | Symlink, oversized file, malformed JSON, nonregular path and changed-during-read must not become evidence |
| Context | Compact stdout contains only approved fields | Candidate prose/injection marker must never appear in stdout or aggregate HTML |
| Relevance | Explicit skill identity or exact path segment | Unattributed report remains unqualified; substring resemblance is not skill use |
| Deduplication | Copied byte-identical file has multiple paths | Different serialization is not automatically a distinct attempt; defer to adapters |
| Rendering | Embedded data hydrates filter/cards/disclosures | Script-closing injection stays text; missing CSS kit clearly degrades |
| Integrity | Input hashes unchanged, new output only | Existing output rejected; source tree output refused |
| Metrics | Known adapter fixture yields exact denominator | Zero denominator -> unmeasured; unknown schema/pass boolean -> no score |
| Identity | Artifact + skill hashes + criteria match | Stale hashes, conflicting results and incompatible cohorts remain separated |
| Fault attribution | Failing author attempt counted | Harness reanalysis does not create a second attempt or become generation improvement |
| Retrieval | Exact returned bytes and repeated-read identities | Incomplete trace -> unknown; file size and wall time cannot stand in for returned tokens |
| Human outcomes | Explicit review response | Selecting a variant alone never becomes a usefulness pass |

## Adapter rollout acceptance (partially implemented)

For each adapter: document owning producer/schema; include a genuine sanitized positive fixture and at least an identity mismatch, omitted criterion, forged completion flag and duplicate/reanalysis fixture. Qualify real CLI entry behavior. Verify rejection logs are compact and privacy preserving. Do not map existing test names to skill KPIs merely by word similarity.

For aggregation: use small hand-calculated datasets with failed/invalid/timed-out attempts, missing responses, historical versions and conflicts. Assert both values and excluded counts. Test monotonicity only where meaningful: adding an observed failure must not improve a success rate; duplicate evidence must not change it. No scalar overall grade.

For context isolation: seed a large private marker in a candidate JSON value. Process the fixture in a subprocess; assert no marker or raw object reaches stdout, HTML or the normalized aggregate. Keep evidence-index metadata bounded. This verifies the deterministic collector boundary, not a future model evaluator's isolation.

## Stop and reporting rules

Retain original failing fixture/output. Fix only the responsible layer, rerun affected checks, and record whether observed evidence changed. No corpus-wide browser matrices for a scanner edit. Missing platform/model tests stay unverified. Do not call the implementation production-ready until adapters, hard I/O supervision, redacted export and representative real-world discovery are qualified.

## v0.2 performed subset

Run scripts/test_adapters.py for 11 synthetic adapter/CLI tests, alongside the eight discovery tests. Current controls cover artifact/source/report/verifier identity mismatch, unknown producer and completion-only flags, omitted/duplicate criteria, missing gates/dependency/companions, reported failure, criterion/gate conflict, duplicate/reanalysis handling, normalized schema rejection, symlink companions and a 100 KB private marker excluded from stdout, normalized JSON, aggregate HTML and report JSON. These are contract fixtures, not a genuine generated delivery or KPI qualification. Other rollout/aggregation matrix items remain pending.

## Genuine frozen compatibility check performed

One official minimal draft was generated by the actual pinned producer CLI, frozen byte-for-byte with producer source snapshot, then checked by scripts/verify_frozen.py. The 11 mutation controls cover stale artifact/report, omitted/duplicate/malformed criterion, forged completion conflict, wrong verifier input, missing gate, unsupported producer, private prose and reanalysis. Scanner entry and privacy/renderer boundary were exercised. A malformed criterion ID first produced TypeError; its raw failing copy and compact result were retained outside the skill. Adapter 1.0.1 now rejects it. Twelve adapter unit tests and eight discovery tests pass. This does not satisfy representative cohort, independent acceptance, full dependency audit or skill-efficacy testing.

## Runtime/lint identity checks performed

Adapter 1.1.0: 18 adapter tests plus eight discovery tests pass. scripts/verify_frozen.py verifies the same read-only genuine freeze with 26 controls (11 previous plus 15 runtime/lint additions), fresh scanner CLI output and privacy boundaries. New controls cover stale runtime/lint report bytes, substituted artifact/manifest/inspected-HTML identities, missing/duplicate startup routes, forged runtime pass despite errors, absent/stale lint source identities, unsupplied policy, forged lint pass despite errors, malformed severity and private runtime/lint prose. Unit controls additionally exercise matching supplied policy, changed policy bytes, malformed route/document fields, warning/unverified preservation and unsafe runtime/lint symlink companions. No gate reproduction, browser run or KPI calculation was performed in this continuation.

## Acceptance identity checks performed

scripts/test_acceptance.py adds 11 tests, for 37 unique unit tests total (11 acceptance + 18 adapter + 8 discovery). Same genuine acceptance-bearing freeze passes 44 mutation controls (26 inherited runtime/lint/static plus 18 acceptance additions), actual scanner entry and private-marker checks. Acceptance controls cover stale/missing companions, wrong artifact/spec/runner/check/scheme identities, omitted/duplicate/substituted cases, omitted/duplicate/malformed results, forged pass or not-applicable claims, generation summary conflict and private prose. Unit coverage adds zero-required-result handling, harness-error attribution, required-flag types, declared-unexecuted false pass, version-1 spec rejection and unsafe acceptance companion symlinks. No semantic completeness, independent evaluation or KPI claim.

## W5 checks performed

Nine split-study unit tests plus the existing 37 tests pass (46 total). The genuine historical packet yields 53 reported scoped observations. Six copy-only normalized controls reject promotion to clean-context success, completed delivery, token/ranking telemetry, confirmed defects, preservation-as-behavior evidence and full-system acceptance. A conflicting contamination flag retains recorded evaluator-access exclusion and behavior observations. Actual CLI rejects changed source bytes privately, including a 100 KB marker, and all original selected source hashes remain unchanged. No author/evaluator execution, broad scan, general aggregation, target change or publication.

## Log-first checks performed

Eight new trace tests pass alongside the eight discovery/renderer tests after the dashboard change. Known historical batch supplies three structurally recognized traces with no producer reports passed to the parser. Test controls distinguish failed exits from task success, deduplicate repeated item records, retain conflicting item identity, detect unresolved/mixed traces, reject substring attribution, bound malformed/large records, protect excluded roots/symlinks, deduplicate exact source copies and keep a private marker out of stdout/HTML/normalized results. No browser QA or provider-wide recall claim.

## Native-log real-use checks

Eight native parser tests, eight log-parser tests and eight discovery/renderer tests pass (24 relevant tests). Controls distinguish catalog mentions, browser-source hints and completed tool calls from actual skill/task acceptance, preserve missing/conflicting results, and protect raw markers. Initial read-regex delay was interrupted before reporting; shell tokenization replaces it, with a long mixed-command regression control. No raw logs, measured skills or earlier evidence were rewritten. Semantic free-text or screenshot assessment and full provider recall remain unverified.

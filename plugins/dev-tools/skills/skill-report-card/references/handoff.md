# Continuation handoff

## User intent

Build skill-report-card: automatically discover relevant local samples without forcing users to locate them, then show a hydrated mini-dashboard of skill goals/KPIs. Evidence processing must not pollute the calling session's context. Initial measured skills: base-ui, component-variants, wireframe-review. Each has one primary goal, secondary goals and 3-8 conceptually distinct KPIs. No automatic evaluations, overall grades or fabricated scores.

## Read order

1. ../SKILL.md for the operational contract.
2. spec.md for boundaries/architecture.
3. kpis.json for the 17 proposed KPI definitions.
4. testing-plan.md, then scripts only for the layer being changed.
5. ../resources/reports/initial-verification.md for actual performed checks and limits.

## Current implementation

- Python stdlib bounded discovery with prioritized automatic roots, explicit overrides, exclusions, JSON limits and exact-copy deduplication.
- Fresh output: evidence-index.json, report-card.json, hydrated index.html and local kit.css.
- Routine stdout is compact metadata; report contents are not sent into conversation context.
- Verified sibling base-ui CSS is consumed when available; otherwise explicit plain HTML fallback.
- All performance KPIs intentionally remain Not measured. Candidate evidence is not qualified, denominators are not invented, semantic evaluation is absent.
- No other skill, original evidence, release archive or peer output was changed by creation.

## Next work, in order

- [ ] Review proposed KPI contracts with the user; set targets/cohort requirements where justified. Preserve the distinction between usefulness, behavior, fidelity, portability, integrity and cost.
- [ ] Add one qualified adapter first: wireframe generation metadata can establish reported delivery mode and gate results, but requires artifact/dependency/acceptance identity to establish delivery integrity. It cannot independently prove task-flow completeness. Inspect a small explicitly bounded sample outside the parent context.
- [ ] Implement versioned normalized observations and schema validation; retain exact provenance, attempt IDs, reanalysis and conflicts.
- [ ] Add attempt-level deduplication and deterministic aggregation with negative controls. Keep unsupported KPIs unmeasured.
- [ ] Add coverage drill-down (searched roots, limits/errors, excluded counts, candidate provenance) without exposing raw report prose.
- [ ] Add hard subprocess timeout/resource supervision and an adversarial filesystem-race review. Current traversal budgets are soft.
- [ ] Improve artifact discovery beyond known JSON filenames (HTML/manifests/feedback), with content-read gates and measured false positives/negatives.
- [ ] Add a redacted share export and retention controls; never silently upload local paths or traces.
- [ ] Run a bounded requested real-system pilot, then compare discovered coverage to a curated sample. Observational selection bias stays explicit.
- [ ] Consider isolated semantic reviewers only with evaluation authorization and available agent permissions. Same-user isolation is not a security boundary. Do not leak evaluator prompts into authors' contexts.

## Work discipline

Do not recursively read samples into the conversation. Use local processes; open the generated dashboard or request a narrowly scoped summarized finding. Do not write adapters that simply trust a top-level pass flag. Do not rerun or relabel old accepted limitations. Keep build work inside this skill; disposable outputs in /private/tmp. No changes to base-ui/component-variants/wireframe-review are authorized by this handoff. Preserve sealed holdouts and unrelated private data.

## Paste to the next chat

Read /Users/kimgranlund/.codex/skills/skill-report-card/SKILL.md and its references/handoff.md, spec.md, testing-plan.md and kpis.json. Continue building the skill from its working discovery-only seed. First verify the current tests, then implement one provenance-qualified adapter and its negative controls before calculating a KPI. Keep evidence processing outside the calling session context; return compact summaries and dashboard links. Do not modify measured skills, existing evidence, accepted limitations, sealed holdouts or peer-owned files. Report exactly what is implemented, tested and still unmeasured.

## Continuation update: v0.2, 2026-10-11

Implemented one pinned reported-observation adapter in scripts/adapters.py and scanner integration. scripts/test_adapters.py adds 11 passing synthetic controls; all eight prior discovery tests still pass. Normalized observations are emitted to fresh observations.json. No performance KPI or denominator is computed. See resources/reports/adapter-verification.md for exact limits.

Next: qualify a genuine frozen positive sample from the pinned producer (currently synthetic positives only), audit runtime/lint/acceptance identities, establish full source/dependency and author-attempt/cohort identity, then implement attempt deduplication and conflict-aware aggregation with its own controls. Do not treat reported stage passes as independently reproduced results. Preserve the historical unsupported sample and initial-verification.md unchanged. Targets remain unset; user review of proposed contracts still precedes KPI evaluation.


## Skill-owned performance contracts

A versioned schema, proposed base-ui example, stdlib validator, rejection tests and adoption procedure are now available in performance-contract-adoption.md. Read it before moving the registry into measured skills. Contract discovery is not implemented; references/kpis.json remains the active proposal source. No measured skill was changed by this addition.

## Continuation update: genuine frozen draft, 2026-10-11

Completed one actual pinned producer CLI run using its official minimal input with --mode draft and browser resolver auto. Fresh output and a read-only frozen snapshot remain under /private/tmp/frozen-adapter-verification-cyh6qafi. No previous sample or original skill source was modified. The prior located matching candidate was our synthetic fixture and was excluded from genuine verification.

scripts/verify_frozen.py verifies the fixed freeze ledger, pinned producer snapshot, actual scanner entry and 11 copy-only controls. All passed. A malformed criterion-ID control first exposed TypeError; retained failing packet now rejects after adapter 1.0.1's shape guard. Twelve adapter unit tests plus eight discovery tests pass. See resources/reports/genuine-frozen-verification.md. Raw packets and logs remain outside conversation and skill resources.

Next: runtime/lint/acceptance identity audits, complete source/dependency and author-attempt/cohort identities, then attempt deduplication and aggregation controls. No KPI or denominator is calculated; all 17 remain unmeasured. This controlled minimal draft verifies mechanical compatibility, not task success or a representative cohort. Prior records and unsupported historical samples keep their original status.

## Continuation update: runtime/lint audits, 2026-10-11

Completed runtime/lint identity audits for the unchanged genuine frozen draft. Adapter is now 1.1.0. Mandatory fixed runtime/lint companions have generation-report hash and subject identity checks; runtime routes must match the emitted manifest; lint source identities match references/lint-sources-v1.json (nine hashes). Conditional fixed policy identity is audited without semantic policy evaluation. Fail/error versus status/exit contradictions remain conflicts. Warning/unverified coverage remains separate.

18 adapter tests and eight discovery tests pass. Same freeze passes 26 copy-only controls with scripts/verify_frozen.py. Fresh output: /private/tmp/frozen-adapter-verification-cyh6qafi/runtime-lint-verified. Raw copies/logs stay there, never in parent context. Original/frozen hashes and previous reports remain unchanged. See resources/reports/runtime-lint-verification.md.

Next: acceptance identity audit using an independently scoped genuine acceptance-bearing frozen output; this minimal draft has no acceptance. Full skill/dependency source identity and author-attempt/cohort qualification remain pending before attempt deduplication or aggregation. Runtime runner identity is absent from this frozen report and cannot be invented. All 17 KPIs remain unmeasured; no gate rerun or model evaluation occurred here.

## Continuation update: acceptance identities, 2026-10-11

Adapter 1.2.0 adds scripts/acceptance.py and references/acceptance-sources-v1.json for version-2 spec identity/coverage audits. New genuine acceptance-bearing output was produced by the pinned CLI in an isolated source/dependency pair with a controlled two-case preview-presence-only spec. Installed producer's derived-index gate failed before isolation; unsuccessful logs/stages were preserved. Only disposable copies were reconciled. A second explicit lint source profile records the isolated cohort; older profile and outputs remain unchanged.

Raw workspace: /private/tmp/acceptance-adapter-verification-4_spdnis. Successful output/freeze/controls: isolated-pair-run/. Fresh final report/dashboard: isolated-pair-run/verified-final/. Seventeen reported observations; all performance eligibility false. 44 frozen copy-controls and 37 unique unit tests pass. Installed base file hashes, new original/frozen output hashes and previous freeze hashes rechecked unchanged. See resources/reports/acceptance-verification.md.

Next: full skill/dependency identities and author-attempt/cohort qualification before deduplication/aggregation. The acceptance spec establishes mechanical preview presence only; evaluator independence, brief coverage and task completeness remain unverified. Version-1 acceptance and broader semantic evaluation remain unsupported. All 17 KPIs remain unmeasured; no target/denominator or overall score.

## W5 update: historical split-consumption qualifications, 2026-10-11

Completed W5 separately from W1-W4. New explicit-batch adapter scripts/split_study.py and verifier scripts/verify_split_study.py register six fixed source selections in references/split-study-v1.json. Reused generation/acceptance discipline without changing adapters.py or acceptance.py. Nine new tests; 46 unique tests pass. Genuine prior packet retains 53 scoped observations, contaminated clean-context eligibility, incomplete draft, five unverified owner observations, byte-classifier limits and preservation/behavior separation. Six promotion controls, conservative contamination conflict and changed-source/privacy rejection pass. KPIs and attempt denominator remain unmeasured/unqualified.

Evidence and raw controls: /private/tmp/reportcard-split-w5-aiko0yx4/verified-final. Main-session handoff: generative-systems/resources/reports/split-consumption-followup-2026-10-11/w5-handoff.md. No W1-W4 edits, author/evaluator calls, target changes or experimental publication. Remaining: structured behavior engine/subject binding, original seal-to-selected-artifact correspondence and full source/attempt applicability before any aggregation. Neither missing evaluator access nor preservation establishes clean-context behavior.

## Log-first direction, 2026-10-11

User directs that skills/repos should be assumed not to emit measurement data. Primary run is now scripts/scan_traces.py; no producer metadata is required. scripts/traces.py parses bounded recorded Codex exec JSONL events and surfaces whole-trace commands/exits/output bytes plus separately scoped usage events. Dashboard displays Observed in logs instead of concealing these measurements behind KPI tiles. Previous producer/acceptance/study adapters are optional corroboration and remain unchanged.

Eight trace tests and eight discovery/renderer tests pass. Scoped pilot reused the prior batch's three execution traces only; no broad scan, author trial or skill instrumentation. Output: /private/tmp/reportcard-trace-discovery-io4_vo3h/dashboard. Logs and originals are preserved; raw content remains outside the chat. Task quality, capture completeness and causal skill attribution remain unverified. Next: add other log formats and identify criterion-specific outcome evidence already in traces; do not require new skill-emitted manifests or targets to measure observable quantities.

## Real-use native logs, 2026-10-11

User-authorized bounded search inspected 272 files, selected 65 relevant entries and analyzed 64 unique streams. Added native_traces.py, analyze_real_use.py and eight tests in test_native_traces.py. Dashboard now surfaces inferred candidate use, missing-brief source access and specific missing KPI evidence. component-variants: 3 candidate turns, 12 missing-brief access turns, 13 reads/192,109 logged bytes. wireframe-review: 4 candidate turns, 54 missing-brief access turns, 38 reads/690,199 bytes. No independent base-ui use qualified in this pass.

No formal performance KPI qualified by this syntax-only pass. Do not infer that every raw log lacks semantic evidence; screenshots/free-text outcomes were not judged. Read bytes are observational proxies, not quality-qualified cost. Output: /private/tmp/reportcard-real-use-33bqmyr0/report. search-coverage.json records unchanged/changed/unavailable original snapshots. No instrumentation, targets or original-log writes. 24 relevant tests pass; old report/acceptance/study work preserved.

## Separate-context semantic review, 2026-10-11

User explicitly authorized semantic delegation. Three separate reviewers inspected selected real-use candidates, older bounded relevance searches and permitted linked evidence. Candidate flags resolved to maintenance/controlled studies rather than eligible consumer attempts. Wireframe28, component12 and base8 initial reviews overlap and must not be summed. No real-consumer KPI denominator qualified; all17 remain unmeasured. Specific gaps and inferred classification confidence are in fresh dashboard /private/tmp/reportcard-semantic-real-use-20261011-final. Prior base reviewer output was preserved and superseded after study-origin reconciliation.

Added scripts/semantic_results.py and nine controls for qualified cohort aggregation, duplicate/conflict handling, missing outcomes, inference/retrospective separation and actual CLI.33 relevant tests pass; failure-count mutation observed red then original green. Source/existing skill evidence remains unchanged. One component log read exceeded32MiB after append; explicitly disclosed, not fully bounded. See resources/reports/semantic-real-use-review-2026-10-11.md. No consumer artifact qualified, no new task/browser trial, no causal/current efficacy or exhaustive recall claim. Next search should target genuinely applied tasks or additional providers; never relabel excluded studies as real-use to fill cards.

## Readability repair, 2026-10-11

User screenshot exposed machine JSON in visible summaries and a string missingEvidence iterated as characters. semantic_results.py now accepts an evidence sentence as one item; integration regression pins the whole sentence. Dashboard shows readable coverage label/value rows, concise evidence-needed copy and nested audit disclosures; no raw JSON blocks in the interface. Original evidence and prior dashboard preserved. Fresh output: /private/tmp/reportcard-readable-20261011. Ten semantic and eight discovery tests pass. Four Chromium checks cover390/1280 widths, light/dark, filter, keyboard disclosure, no horizontal overflow or page errors. Screenshots visually inspected. No new evidence evaluation or measurement changes; Safari/AT unverified.

## Controlled-test measurements, 2026-10-11

User authorized test runs as a separate population. Three separate semantic reviews qualify5 KPIs: component fairness, preview operability, feedback fidelity, decision usefulness; wireframe task completeness. Historical reported/inferred origin has medium confidence;1/1 explicit human review session has high confidence. Initial failures and repaired phases remain separate; two human messages collapsed into one session. Base-ui stays unmeasured. No real-use improvement or overall score.

Fresh dashboard /private/tmp/reportcard-controlled-tests-20261011-final; full compact record resources/reports/controlled-test-kpis-2026-10-11.md. Original evidence, old reports and superseded reviewer files preserved.13 semantic+8 discovery checks pass; mixed-population bypass mutation observed red, original green. Four Chromium dashboard checks pass. No new author/efficacy trials. Cases are metric units/eligibility diagnostics, not author-attempt counts. Population conflict rejection and unit-specific telemetry guard now implemented. Evidence confidence is subjective and historical; full source identity/capture completeness and independent behavioral reproduction remain unverified.

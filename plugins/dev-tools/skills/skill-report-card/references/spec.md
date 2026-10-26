# Skill Report Card specification

Version 0.2, 2026-10-11. Status: discovery/renderer plus one reported-observation adapter; performance aggregation remains unimplemented. This file is the continuation authority, not a claim of completed KPI evaluation.

## Outcome and scope

Produce a small hydrated local HTML dashboard showing what selected skills accomplish, what local evidence supports that judgment, where evidence is absent and what should be investigated next. Automatically find relevant samples without asking users to curate every path. Do not fill the calling conversation with those samples.

Three initial skill definitions are in kpis.json: base-ui (5 KPIs), component-variants (6), wireframe-review (6). Each has exactly one primary goal and supporting secondary goals. Definitions are versioned proposed contracts, not assertions extracted from the skills. Do not edit the measured skills to install these definitions. Later, skill-owned declarations may supersede defaults only through explicit reconciliation/versioning. Base-ui results may appear as dependencies of review artifacts but must not count twice in a composite score. No overall score in v1.

## Implemented pipeline

1. scripts/scan.py discovers likely roots automatically and visits directories breadth-first within each root. Prioritized roots precede broader home discovery. Explicit --root replaces defaults.
2. Metadata/name filters admit bounded JSON files only. Reads use no-follow file opens, reject nonregular files and oversized records, and detect basic size/mtime changes while reading. Directory symlinks are skipped.
3. Relevance uses exact skill path components or selected structured identity fields. Hints do not establish causal use. Unknown schemas remain unqualified. The pinned adapter is described below. No recursive scan of arbitrary string values for commands or instructions.
4. SHA-256 of complete accepted bytes groups exact duplicate documents. Paths remain aliases. This is document deduplication, not attempt deduplication.
5. evidence-index.json records candidates, bounds and coverage. observations.json holds versioned reported observations; report-card.json holds goals and unmeasured KPIs. The renderer embeds only this compact aggregate; raw samples never enter HTML or stdout.
6. HTML uses verified sibling base-ui CSS when available and textContent for dynamic labels. No HTTP service, network request, dependency download or remote analytics. A missing styling kit yields plain HTML with the limitation disclosed.

Default limits: 30 seconds best-effort, 100,000 entries, 3,000 candidate files, 2 MiB per candidate, depth 18. Report skipped/error/limit counts. Bounds are operational limits, not sampling representativeness. Root order and filesystem ordering can bias candidates. A blocked filesystem operation may exceed the soft wall-time budget; hard subprocess supervision is a follow-up.

## Context boundary (mandatory)

The collector runs in a separate local process. Return only status, dashboard/index paths, candidate count, measured KPI count and stop reason. No raw excerpts, per-file listings, stack traces containing evidence or candidate prose in routine tool output. Keep routine stdout below 4 KiB. The host response should link the dashboard and summarize at most five findings. Never `cat` the evidence index or large reports into the calling context.

When semantic judgment is needed, use a separate bounded evaluator context only when that host permits delegation and the user has authorized evaluation. Provide one scoped evidence packet with artifact identities and an agreed rubric; return small structured findings with citations. No evaluator dispatch is implemented. This side conversation cannot launch agents. Deterministic scan isolation is not an OS security sandbox and does not guarantee zero context cost: the compact results and tool metadata still occupy context.

## Collection exclusions and privacy

Exclude credential/key stores, .env, unrelated chat/session databases, .claude private trees, sealed/holdout paths, Library, dependency trees, VCS internals and symlinks, including explicitly passed roots. Do not relax exclusions automatically when few results appear. No elevated access, credential reading, discovered-script execution or content-driven paths. Root discovery is filesystem-only in v0.1; no Spotlight/OS-index API. Entire .claude trees are conservatively skipped because this environment has private subtrees there.

Write only to a fresh output directory, mode 0700. Do not write under the installed skills root; do not mutate or relocate input evidence. Local metadata can contain sensitive absolute paths; dashboards must warn before users share the index. Export/redaction is not yet implemented. Native permissions may prevent reads; report partial coverage without prompting for escalation. Persist no machine-specific root configuration in the shipped skill.

## Required next-stage evidence model

Implement adapters with a registry keyed by producer/schema/version. An adapter must be explicitly selected by structural validation, never filename alone. Each normalized observation needs:

- skill ID, skill source/dependency identities and metric-contract version;
- attempt ID, artifact ID/hash, phase (generation/revision), predecessor when applicable;
- criterion ID and observation outcome: pass/fail/unverified/not-applicable;
- evidence file hash, structured selection (e.g. JSON pointer), adapter version;
- report origin: reported, independently reproduced or explicit human response;
- task/cohort, model/effort if applicable, environment and observation time;
- accepted limitations, missing data and applicability to the current skill;
- telemetry units and completeness, when measuring cost.

Hash correspondence does not prove report truth. Discovered instructions and claims remain untrusted source data. Qualifying historical reports does not automatically make them current. Timestamps and path names cannot substitute for skill/artifact identity.

Deduplicate observations by attempt/criterion/environment identity after qualification. Conflicting observations remain visible; do not select whichever makes the score higher. Reanalysis of the same submission is a new interpretation, not another author attempt. Failing, timed-out and invalid submissions stay in eligible denominators. Missing evidence and nonresponses have separate coverage counts. Never treat source checks, test cases, screenshots or copies as independent generation attempts.

## KPI calculation and targets

Use definitions in kpis.json. Validate numerator <= denominator for proportions and require nonzero eligible denominators. A null target produces an observed result with no meets-target judgment; do not invent a threshold. Compare only compatible cohorts and show excluded cohort counts. Bytes, model tokens, tool calls and time are different units. Report p50 context bytes and repeated-read share only with complete read traces, conditioned on declared quality criteria, with failed/excluded attempt counts alongside.

State axes are independent:

- Performance: meets-target / below-target / mixed / no-target / not-measured / not-applicable.
- Evidence: current / historical / stale / insufficient / conflicting.

An accepted limitation is not a pass. A correctly disclosed draft may pass delivery integrity and fail task completeness. Decision usefulness requires an explicit reviewer response; preference selection alone is not a proxy. Distinctness/fairness use predeclared human rubrics, not DOM-difference percentages. Shell overhead requires defensible effort attribution, not generated LOC or file mtime.

## Dashboard acceptance

Skill filter, primary/secondary goals, 3-8 KPI tiles per skill, result with numerator/denominator and unit, target, evidence strength, cohort/window, dependency version and bounded trend where valid. Each tile reveals definition, evidence references, limitations and actionable missing measurement. Discovery panel exposes roots, exclusions, budget termination, errors, candidates, duplicates and attribution status in a human-readable view; v0.1 links the machine-readable index instead of a complete coverage inspector. Never render evidence HTML inside the dashboard. Use safe text and vetted local links. No interpolated untrusted HTML, external scripts or tracking.

Charts must not hide zero denominators, missing periods or version breaks. Start with cards/tables; charts are optional. Provide keyboard, narrow-screen and no-script access (JSON fallback initially). A screenshot is supplementary; the hydrated artifact is the deliverable.

## Evidence and change policy

All authoring/verification fixtures belong in /private/tmp. Retain a small checked report in resources/reports when needed; never import another skill's historical corpus. Do not modify measured skills, existing evidence, sealed holdouts, release ZIPs or peer-owned outputs as part of reporting. Publication, adapter expansion, browser execution and model evaluation have separate scopes. Discovery is read-only; reports are fresh artifacts.

## Implemented adapter: wireframe-generation/1.2.0

Registry identity is the producer SHA-256 pinned in scripts/adapters.py. The producer has no explicit schema version, so this is a single audited source snapshot, not a general wireframe schema matcher. Structural validation is mandatory after producer selection. The hash identifies the declared producer; it does not authenticate authorship or prove truthful reporting.

Fixed sibling reads: artifact.html, manifest.json, source.manifest.json, verification.json, runtime.json and lint.json; lint-policy.json is read only when the generation report declares a supplied policy. No source-provided path is opened. Each companion shares the collector exclusion/no-follow checks and per-file byte bound; at most nine companions are read per unique supported candidate, with soft time checks before reads. Counts disclose companion bytes/reads/errors. Missing, oversized, symlinked, malformed or mismatched inputs cannot qualify. Directory races and hard I/O supervision remain unresolved.

Qualification binds artifact bytes, original source-manifest bytes, verification-report bytes and the verifier's artifact/manifest input identities. All seven named static criteria and all expected stage rows must exist exactly once. Dependency content identity is retained as reported; installed dependency bytes and complete skill source identity are not reproduced. Stage exits remain reported claims. Runtime/lint report subjects are audited as described below. Supplied version-2 acceptance subjects and declared coverage are audited as described below. Top-level completion flags never establish success. Static criterion/gate contradictions produce a conflicting state with both observations retained.

Normalized observations have schemaVersion 1 and a strict whitelist validator. They retain evidence hashes, exact structured selections and adapter identity. Unknown task, author attempt, full skill source, environment, model/effort, observation time and telemetry remain null with explicit missing-data reasons. Raw prose, stdout, stderr, accepted-limitation text and arbitrary identifiers are not copied to normalized output. Original limitations stay in original evidence; no limitation is converted to a pass. Raw input evidence is unchanged.

Reported mode is retained in candidate adapter metadata. Delivery integrity is always unverified. Task-flow completeness is never inferred. All performanceEligible flags are false and all 17 KPI values remain null. Byte-identical copies share one candidate; differently serialized reanalyses may retain multiple evidence documents but never become author attempts. Attempt deduplication and aggregation are intentionally deferred. No denominator or targets are calculated.

Synthetic fixture coverage is recorded in resources/reports/adapter-verification.md. The bounded historical resource sample remains unsupported. One actual pinned CLI output, using the official minimal input in draft mode, is now frozen and adapter-verified with 11 mutation controls; see resources/reports/genuine-frozen-verification.md. Runtime/lint identity audits subsequently passed against that unchanged freeze; see resources/reports/runtime-lint-verification.md. Representative real-world adapter qualification remains unverified. This controlled input is not evidence of author-task efficacy.

## Frozen compatibility verifier

scripts/verify_frozen.py accepts an explicit local frozen directory and a fresh output directory. It bounds reads to fixed filenames, refuses symlink paths, checks the freeze ledger and pinned producer snapshot, runs the adapter and scanner CLI, and exercises 11 mutations only on new copies. Raw control packets stay in the disposable output; stdout contains counts and output links only. The frozen receipt records observed local CLI execution provenance; it is not authenticated third-party attestation. Adapter 1.0.1 adds a criterion-shape rejection before set construction, fixing the observed malformed-ID exception without changing valid-output qualification or KPI eligibility.

## Runtime and lint identity audit: adapter 1.1.0

Runtime report bytes must match generation.reports, and its artifact/manifest input hashes must match the actual frozen subjects. Required startup routes are derived from the emitted manifest using the pinned producer's page-selection and desktop/mobile iteration. Empty, missing, duplicate, extra or malformed routes cannot qualify. Reported errors determine the startup-gate outcome; inconsistencies with runtime status or stage exit remain conflicts. Runtime's report lacks a runner/source/browser-version identity, so execution provenance and reproducibility remain unverified.

Lint report bytes must match generation.reports, and both input and inspected-HTML hashes must match the artifact. All nine declared source identities must exactly match one registered profile (references/lint-sources-v1.json or lint-sources-v2.json), recorded only after correspondence with frozen report and installed source bytes was checked locally. This is a pinned source-identity contract, not a complete skill/dependency snapshot. Non-null temporary builds are rejected for this producer's fixed HTML path. A supplied policy requires correspondence between generation identity, lint identity and fixed sibling policy bytes; policy contents are not semantically evaluated. No-supplied-policy and null report policy must agree.

Lint findings must use recognized severities and typed structured fields. Errors determine the reported lint error gate, while warning/unverified counts remain separate. The frozen positive retains one unverified finding; it is not promoted to a pass. Missing, unsafe or mismatched runtime/lint companions now reject qualification. Two new reported observations have exact report-hash/pointer provenance (/errors and /findings), bringing this freeze to 15. Raw error/finding prose, route labels, paths, browser strings and limitation prose are never copied into normalized results. All performance eligibility flags remain false.

## Acceptance identity audit: adapter 1.2.0

Supplied acceptance requires fixed sibling acceptance.json and acceptance-report.json. Generation spec/report hashes, report artifact/spec subjects and pinned runner/check-library/scheme hashes must correspond. The current registry supports report version 1 with spec version 2, string IDs in a bounded identifier grammar, exact unique case/result coverage, requested case identity, required-flag types and applicability/dependency structure. Version 1 specs remain unsupported. No evidence-provided path is followed. Conditional reads bring the maximum to nine fixed companions per supported candidate.

The audit derives scoped required-case outcomes from result records rather than top-level pass flags. Assertion/application failures remain failures; unsupported, blocked, harness/setup errors and declared unexecuted requirements remain unverified. Zero required applicable results cannot become a pass. Contradictions with report pass/delivery status, generation delivery status or acceptance-stage exit remain conflicts. Declared requested case fields are audited; actual scheme correctness, semantic check implementation, brief coverage and evaluator independence are not reproduced or inferred.

One additional reported observation uses acceptance-report SHA-256 and /cases. This acceptance-bearing sample has 17 observations, performanceEligible false, delivery-integrity unverified, and no KPIs. The controlled presence-only spec is not an author-task acceptance study. Runner/check/scheme snapshots are frozen; hashes identify recorded implementations without authenticating reported truth.

The genuine output required a disposable source/dependency pair because installed derived token-index freshness failed. Only the isolated pair's derived index/descriptor/compatibility mirrors were reconciled; producer bytes retain the original pin. Two resulting lint source hashes differ from the older profile. Profile v2 was registered after all nine hashes matched isolated snapshot bytes; profile v1 and previous evidence remain intact. This separate dependency/source cohort cannot imply improvement or transfer to installed sources. Failure logs and earlier staged runs remain retained outside chat.

## W5 historical split-study interpretation

scripts/split_study.py is a separate explicit-batch adapter, split-consumption-study/1.0.0. references/split-study-v1.json pins six exact structured source selections in the authorized historical batch; no broad search is part of its CLI. Each source and adjacent generation subject is bounded to 2 MiB, no-follow reads, size/mtime checks and exact registered hashes. No holdout content, evaluator code, author trace or artifact HTML is rendered or executed. The explicit sealed-author-submission metadata selection is a task-specific exception, not a change to discovery exclusions or an enforced sandbox.

The packet yields 40 selected revision behavior observations (five checks, two alternatives, four width/scheme cases), one contaminated clean-context eligibility observation, one incomplete-draft delivery observation, five unverified unknown-style-owner observations, three command-return byte observations and three reported preservation observations: 53 total. Behavior engine identity and behavior-to-artifact binding remain unverified in these structured selections. The generation artifact's declared hash is reproduced; original seal/behavior subject correspondence is not independently established.

All observations retain source IDs, hashes and exact structured pointers. No source prose, arbitrary command text or raw telemetry usage is copied. Preservation cannot supply behavior provenance. Conflicting protocol contamination metadata cannot override recorded evaluator access. Missing access alone cannot establish clean context. Unknown style ownership cannot be a confirmed defect. Mixed command-return bytes cannot be relabelled model tokens or used as cross-task rankings. Draft gates cannot become delivery acceptance or full-system acceptance. Normalized output uses a whitelist schema and remains performanceEligible false with null attempt denominator and zero measured KPIs.

scripts/verify_split_study.py retains six dimension-promotion controls, one conservative metadata conflict and a changed-source/private-marker CLI rejection in fresh temporary output. The historical narrative is not a KPI denominator, and this adapter does not introduce general aggregation, targets, auto-discovery or another trial.

## Primary evidence policy: logs and use traces

User direction: assume skills and repositories do not capture measurement data. Trace analysis is now the primary entry point (scripts/scan_traces.py); producer manifests and structured study reports are optional corroboration. No measured skill/repository instrumentation is required. Observed quantities can be reported without KPI targets; criterion-specific quality/attempt denominators remain necessary only for the performance measures that require them.

scripts/traces.py parses recorded Codex exec JSONL events in a local process. Only terminal command items yield measurements. Exact repeated terminal items count once within a trace; conflicting records for the same command ID remain visible and their outcome/byte totals are excluded. Failed exits stay visible. Unresolved started items and mixed-thread identities are coverage limitations, not success. Command-path references provide explicit relevance hints, not causal attribution or proof of source reads. Raw command strings, aggregated output, messages and thread IDs never enter normalized output; thread identity is hashed.

Logged decoded UTF-8 command-output bytes and logged turn usage counters have separate units/scopes. A read-containing-command heuristic remains labelled mixed/incomplete. No conversion from bytes to model tokens or attribution of all trace cost to a skill. Capture completeness and truncation remain unverified. Logs do not establish behavior correctness merely because commands exit zero.

Collection defaults: skill-previews and Projects, 20-second soft wall time, 50,000 entries, 100 trace files, 8 MiB per trace, depth 8; parser bounds 10,000 records and 2 MiB per line. JSONL/NDJSON only. Credentials, unrelated session/chat stores, holdouts, symlinks and existing report outputs remain excluded. Explicit roots permit scoped analysis without a system-wide scan. Source copies deduplicate by exact hash; author-attempt aggregation remains absent.

Dashboard now displays Observed in logs separately from performance tiles. Each skill's trace list refers to whole traces that contain a command path reference. Shared traces are not independent skill costs and are not pooled into a grade. Prior report/acceptance adapters and their evidence remain intact.

## Beyond-batch native-log analysis

Explicit user authorization scoped a .codex/sessions search to tool-record references for three skills. Generic discovery still excludes unrelated session stores. Native parser handles call/result pairing, turn boundaries, duplicates/conflicts, and keyword-based categories without returning raw messages or code. Eight tests include catalog-only mentions, private markers, missing returns, source hints that do not become task acceptance, and long compound reads.

This bounded search inspected 272 files from a 538-file metadata inventory and selected 65 relevant entries; 64 unique streams were analyzed. Current conservative result: component-variants three candidate turns plus 12 source-access turns missing brief; wireframe-review four candidate turns plus 54 missing-brief access turns. Base-ui had no independent use qualified outside reporting. These categories are inferences. Native source records may move or append while the app is active; exact read hashes and recheck coverage are retained.

Observed logged single-skill reads: component-variants 13 calls/192,109 bytes; wireframe-review 38 calls/690,199 bytes. Counts include the missing-brief observational subset. Compound/multi-skill reads are excluded. Logged wrapper strings are not model tokens, complete context capture or causal skill cost. No formal performance KPI was qualified by this syntax-level pass: criterion/effect/artifact bindings, quality gates and denominators remain unqualified. This does not prove every raw log lacks semantic evidence. The dashboard shows those facets and specific missing evidence separately.

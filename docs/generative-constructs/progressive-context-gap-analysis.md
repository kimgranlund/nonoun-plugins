# Progressive Context gap analysis

Recorded: 2026-10-05. Ticket T-0247. Method: the generative-systems skill (tier model T0 to T12, review rubric, gap-analysis template). Nothing here changes the plugin or its specs.

Labels on every claim: **[O]** observed in a file read for this analysis (path:line); **[E]** established outside this repository (named); **[I]** inference. Paths are relative to the repository root. `PC` means `plugins/progressive-context/skills/progressive-context`.

## Scope

- System: the `progressive-context` plugin 0.1.2 (one skill, six references, one example), its proposal set in `docs/generative-constructs/`, and how SDLC Lite consumes it (`PC/references/sdlc-lite.md`, `plugins/sdlc-lite/scripts/onboard.py`, `.sdlc/AGENTS.md`, `docs/layout.md`, `docs/docs-schema/design.md`).
- Harnesses: Claude Code and Codex [O `plugins/progressive-context/.codex-plugin/plugin.json:8`]; a browser JavaScript harness exists only as a proposal [O `docs/generative-constructs/04-context-and-harness.md:25-38`].
- Workflows: author a capability contract, assess it against evidence, qualify it for reuse, leave a navigation route [O `PC/SKILL.md:10-18`].
- Rendered targets: none ship. A2UI is optional guidance and "the plugin does not supply a renderer" [O `PC/references/a2ui.md:3`].
- Skipped tiers: T9 (generative UI runtime) and T4 (composition) do not apply to the shipped scope, because the only composition material is the optional A2UI route [O `PC/references/a2ui.md:3`]. T5 (intent) is scored, since the contract's Intent section is the only intent structure.

## Executive assessment

Progressive Context is an authoring skill, "not a lifecycle runtime or execution engine" [O `plugins/progressive-context/AGENTS.md:3`]. Its core is three things: entry-file routing [O `PC/SKILL.md:8,18`], a small capability contract [O `PC/references/contracts.md:5-33`], and an assessment bound to an exact revision [O `PC/references/evidence.md:3-9`]. It states its limits honestly: a skill file alone cannot guarantee immutability, freshness or resource loading, and a filesystem-only deployment should report those as process claims [O `docs/generative-constructs/progressive-context-plugin.md:179`].

Strengths: evidence discipline (`not assessed`, `failed`, `stale`; a change invalidates affected claims only [O `PC/references/evidence.md:13`]); qualification means an independent consumer exercise, never a status flag [O `PC/references/evidence.md:27`]; host-loading facts were probed rather than assumed [O `docs/validation/nested-entry-file-loading.md:39-41,66-70`].

Root constraint: everything is prose guidance. The skill says to add no registry, state machine or schema engine "without an actual need" [O `PC/SKILL.md:24`], so there is no machine-readable manifest, no registry, and no validator beyond packaging checks [O `plugins/progressive-context/AGENTS.md:11`].

Highest-impact gaps: (1) no deterministic check for any rule it states, so drift is only caught by reviewers; (2) the core artifact, the capability contract, has no adoption in the two repositories available here; (3) the context a run actually loaded is not recorded.

Evidence for gap 1, all from this repository's own runs: a hand-numbered guard list in `scripts/check.py` carried two guards 17 and two guards 18 until it was caught [O `docs/validation/release-0.20.6.md:13`]; a closed ticket still held the bug template's placeholder text [O `.sdlc/verify-0224/verifier-L3.md:15`]; a live-run record cited file contents that no committed file backed [O `.sdlc/verify-0229/verifier-L3.md:11`].

Evidence for gap 2: `git grep` for a contract header (`ID: <ns>/<name>`) over tracked files finds only the format example in this repository [O `PC/references/contracts.md:7`], and none in `/Users/kimgranlund/Projects/maison/ui-kit-maison` (its `.sdlc/` is git-ignored [O maison `.gitignore:6`], so ticket text there is not searched). Maison mentions "progressive context" only as its own gen-ui concept [O maison `.agents/skills/gen-ui-manifests/SKILL.md:17`], not this plugin. [I] Contracts are not in use yet.

## Rubric score

Scores use the rubric's 0 to 3 scale per tier [O `/Users/kimgranlund/.claude/skills/generative-systems/references/review-rubric.md:1-8`]. They are my reading of the files cited in the tier map. [I]

| Tier | Score | Tier | Score |
| --- | --- | --- | --- |
| T0 Foundations | 1 | T7 Harness | 1 |
| T1 Capabilities | 2 | T8 Skills and agents | 2 |
| T2 Registries | 1 | T10 Validation | 1 |
| T3 Semantics | 1 | T11 Memory | 2 |
| T5 Intent | 2 | T12 Governance | 1 |
| T6 Context | 2 | Total (ten scored tiers) | 16 of 30 |

Scaled to the rubric's twelve tiers this is about 19 of 36, in the "emerging structured system" band (13 to 24) [O rubric, Interpretation section; scaling is my inference].

## Tier map

| Tier | Current state | Gap | Severity | Recommendation |
| --- | --- | --- | --- | --- |
| T0 | Stable IDs are advised: "the path is a locator, not identity" [O `PC/references/contracts.md:35`]. No namespace or ID grammar beyond the `billing/invoice-review` example [O `contracts.md:7`]. | No schema for an ID, no uniqueness check. | M | R1 (kinds as ids), R7 |
| T1 | A markdown contract with fixed headings [O `contracts.md:5-33`]. The `.claude-plugin` and `.codex-plugin` manifests describe the plugin, not capabilities [O `plugins/progressive-context/.codex-plugin/plugin.json:1-20`]. | Fields are prose; a tool can only regex them. | M | R7 before any schema |
| T2 | None, by design [O `PC/SKILL.md:24`]. The proposal set designs `discover`, `inspect`, `read` over a catalog [O `04-context-and-harness.md:29-33`], unbuilt. Entry files act as informal indexes [O `PC/SKILL.md:18`]. | A project with many contracts can only grep. | L, but only if contracts get used | Do not build (see below); R1 for docs and `.sdlc` |
| T3 | Domain profiles are "a small optional vocabulary", "not a second core ontology" [O `contracts.md:39`]. An ontology and record model are proposed [O `02-construct-model.md:5-66`]. | Profile schema is open [O `progressive-context-plugin.md:271`]. | L | Leave open; R8 reconciles vocabularies |
| T5 | The contract's Intent section, with unknowns named rather than filled [O `PC/SKILL.md:13`]. | No intent IR, which a prose-only skill does not need. | L | None |
| T6 | Progressive disclosure tables exist twice [O `04-context-and-harness.md:13-18`; `progressive-context-plugin.md:157-163`]. Nested-entry loading was probed on both hosts, one trial per arm [O `nested-entry-file-loading.md:3`]. "A file named AGENTS.md is not proof it was loaded" [O `PC/SKILL.md:8`]. | Nothing records what a session actually loaded; the proposal wants "the actual resources loaded by a run" shown [O `04-context-and-harness.md:76`]. | H | R3, R4, R2 |
| T7 | No runtime; the skill needs "no model mapping, subagents, hooks" [O `plugins/progressive-context/AGENTS.md:9`]. The spec splits skill guidance from harness enforcement [O `progressive-context-plugin.md:171-179`]. | The enforcement column has no implementation. | M | R3, R4 supply the small enforceable parts |
| T8 | One shared skill, no agents. Optional routes load only when needed [O `PC/SKILL.md:32-38`]. | None material. | L | None |
| T10 | Packaging checks and a skill validator [O `plugins/progressive-context/AGENTS.md:11`]. "Schema validation establishes structural validity only" [O `evidence.md:13`]. Assessments are written by hand. | No link, ID or drift check; the proposal lists required checks [O `04-context-and-harness.md:80-86`] that nothing runs. | H | R4, R6, R1 |
| T11 | Lifecycle views derived from facts, not stored; stale evidence kept as history [O `PC/SKILL.md:26`; `evidence.md:15-25`]. | Nothing detects staleness; no rule promotes a work record into durable knowledge. | M | R5 (in the docs schema), R9 |
| T12 | Provenance concepts cited (W3C PROV [O `docs/generative-constructs/README.md:45`]); an inspection surface is proposed [O `04-context-and-harness.md:74-78`]. SDLC Lite records `routing_reason` per run [O `plugins/sdlc-lite/scripts/run.sh:520-524`]. | Why a role was routed is recorded; what it read is not. | M | R3 |

## Critical distinctions

| Concept | In Progressive Context today |
| --- | --- |
| Schema | None. |
| Manifest | The plugin manifests only. A contract is manifest-like but prose [O `contracts.md:5-33`]. |
| Registry | Deliberately absent [O `PC/SKILL.md:24`]; proposed in the spec set. |
| Taxonomy, ontology | No taxonomy. An ontology is proposed [O `02-construct-model.md`] while the skill disclaims a core ontology [O `contracts.md:39`]. |
| Recipe, pattern | A stage-based workflow definition and one example [O `PC/references/workflow-stages.md:5-24`; `examples/small-repository-change.md`]. |
| Skill, agent | One skill, no agents. They are kept separate. |
| Harness, validator | Out of scope; no validator. |

Ambiguity to resolve: the proposal set says "construct", "revision" and "instance" [O `02-construct-model.md:5-14`] while the shipped skill says "capability", "contract" and "assessment". The README says the six numbered documents "preserve the initial proposal" [O `docs/generative-constructs/README.md:21`] yet still lists them as the reading order [O `README.md:7-14`]. [I] A reader of the specs cannot tell which words the shipped skill uses. See R8.

## Coupling analysis

- Harness-specific facts that should be portable declarative knowledge: Claude Code loads a nested `AGENTS.md` only through a `CLAUDE.md` import; HTML comments are stripped for Claude Code and kept by Codex [O `docs/repo-onboarding/layered-context-pattern.md:40`; `nested-entry-file-loading.md:66-70`]. These live in onboarding references, not in the skill that tells agents to read entry files. See R9.
- Knowledge duplicated across documents: the progressive disclosure table (two copies, see T6) and the lifecycle description [O `evidence.md:17-23`; `03-lifecycle-and-evaluation.md:5-9`]. [I] Two copies of one table drift.
- Framework-specific knowledge: kept out of the core by routing A2UI and the browser harness through optional references [O `PC/SKILL.md:32-38`]. This is the strongest separation in the system.

## Missing structures

- Typed contracts: a parseable contract header (front matter) instead of an `ID:` prose line [O `contracts.md:7`].
- Discovery: any list of contracts. Entry files hold links only.
- Semantics: a domain profile schema, still open [O `progressive-context-plugin.md:271`].
- Validators: entry-file import and link resolution; no check that every folder with an `AGENTS.md` has a `CLAUDE.md` importing it, although the loading probe shows that is required [O `layered-context-pattern.md:40`].

## Context engineering risks

- Context overloading: low in the skill (small entry files), but SDLC Lite entry files are bounded only by a 60-line target in `onboard.py` [O `docs/docs-schema/design.md` commit `5a1165e`, subject line "use onboard.py's existing 60-line entry-file target"].
- Hidden dependencies: loading differs by host (see coupling).
- Stale knowledge: defined, not detected [O `evidence.md:13`].
- Poor entry points: this repository's `docs/` had 5 loose files and no schema [O `docs/docs-schema/design.md:10`].
- Weak provenance: loaded context is unrecorded (T12).
- Duplicated rules: see coupling.

## The pattern applied to docs/ and .sdlc/

Progressive Context says "add no registry ... without an actual need" [O `PC/SKILL.md:24`]. The need for `docs/` and `.sdlc/` is evidenced here: the schema design cites a thin default layout, a repository that does not follow it, and no rule for what may live in `.sdlc/` [O `docs/docs-schema/design.md:9-12`]. The registry belongs in SDLC Lite, not in Progressive Context, which "stays domain-neutral and keeps its rule against a prescribed folder tree" [O `docs/repo-onboarding/design.md:195`].

| Progressive Context idea | docs/ and .sdlc/ application |
| --- | --- |
| Capability contract | A registry row per kind: holds, does not hold, why, naming, lifecycle |
| Stable id, path as locator [O `contracts.md:35`] | The kind is the id; the folder name may differ [O `docs/docs-schema/design.md:138-139`] |
| Entry file routing | A folder's `AGENTS.md` plus a one-line `CLAUDE.md` import [O `design.md:126-127`] |
| Evidence-bound assessment | The placement proof: fresh sessions given only a path place a hidden-answer brief |
| Stale evidence | A drift check between the machine-readable source and the rendered block |
| Qualification by independent consumer [O `evidence.md:27`] | Placement tested on Claude headless, Codex and an interactive session |
| Memory promotion (T11) | Promotion by copy with a `source:` key |

Cross-check against `docs/docs-schema/design.md` (v0.2 as merged at `5a1165e`; a revision is in review and may already change items b to d):

- **Agrees:** one machine-readable source (`## Kinds` in `docs/layout.md` [O `design.md:138-147`]); entry files with the import [O `design.md:126-127`]; named deterministic checks with negative controls [O `design.md:153-175`]; promotion into `docs/`; a boundary check in both directions [O `design.md:171-173`].
- **(a) Conflict:** a home gets an entry file only at two or more documents [O `design.md:127`], but a registry needs its row in `docs/AGENTS.md` from day one. Keep the row at the root unconditionally; keep the per-home file optional.
- **(b) Missing:** `## Kinds` binds a folder to a kind but the kind's own row (holds, does not hold, why, naming, lifecycle) exists only as prose and tables [O `design.md:54-70,138-147`]. Define the row schema in the layout file.
- **(c) Missing:** no drift check between the layout file and the rendered `docs/AGENTS.md`. The managed-block mechanism with a version and hash already works for the `.sdlc` router [O `.sdlc/AGENTS.md:1`]; extend it.
- **(d) Missing:** `.sdlc` record types are hard-coded in a check (`B-2a` [O `design.md:172`]), not held in a registry. Give `.sdlc` the same registry source so one parser serves both.
- **(e) Missing, being added:** the placement proof is not in v0.2; the revision in review adds it.

## Ranked improvements

Ranked by evidence of repeated failure in this repository, then by cost. "Det" means script-checkable; "Judg" means judgment.

1. **R1. One registry row schema and a drift check for docs and .sdlc** (T2, T10; M; Det). Files: `docs/docs-schema/design.md`, `plugins/sdlc-lite/scripts/onboard.py`. Risk: entry-file size. Why: hand-kept lists drift [O `release-0.20.6.md:13`]; the managed block works [O `.sdlc/AGENTS.md:1`]. Covered by tickets T-0241 and T-0242; extend their handoffs.
2. **R2. Placement proof harness** (T6, T10, qualification; M; Det scoring, Judg briefs). Files: a new script and a validation record. Risk: small samples, model cost. Why: the loading probe had one trial per arm [O `nested-entry-file-loading.md:3`]. Filed by the docs-schema pass.
3. **R3. Record which context a run loaded** (T12, T6; M; Det). Files: `plugins/sdlc-lite/scripts/run.sh`, trace ingestion. Risk: Codex rollout files were absent for some runs [O `docs/validation/codex-conductor-solo-live-run.md`, limits]. Why: only the routing reason is stored [O `run.sh:520-524`].
4. **R4. Entry-file resolver** (T10; S; Det). Files: a new script or `onboard.py check`. Checks: every `AGENTS.md` has a `CLAUDE.md` importing it, every link and import resolves, size target met. Why: Claude Code loads nested files only through the import [O `layered-context-pattern.md:40`].
5. **R5. Promotion rule** (T11; S; Judg). In the docs-schema design as promotion by copy; ticket T-0245. No new work.
6. **R6. Handoff and evidence lints** (T10; M; Det). Files: `tickets.py check`, a docs evidence-link check. Checks: no template placeholder text in a closed ticket; every evidence path a record cites exists in git and is not ignored. Why: both failures happened [O `.sdlc/verify-0224/verifier-L3.md:15`; `.sdlc/verify-0229/verifier-L3.md:11`]. Risk: false positives, so start as warnings.
7. **R7. One real capability contract** (T1; S; Judg). Write a contract and assessment for one SDLC Lite capability (for example the solo lane) using `contracts.md`, to learn whether the format holds. Why: no contract exists to learn from (see gap 2).
8. **R8. Reconcile the two vocabularies** (T0, T3; S; Judg). Add a status banner to each numbered spec pointing at the shipped skill, and a glossary mapping construct to capability. Files: `docs/generative-constructs/*.md`.
9. **R9. A portable host-loading matrix with a re-probe script** (T7, T10; M; Det). The facts in `nested-entry-file-loading.md` were a one-time manual probe; host versions change.
10. **R10. Evidence staleness report** (T11; M; Det). For validation records that bind a plugin commit, list those whose bound paths changed since. Why: "stale" is defined but nothing detects it [O `evidence.md:13`].

Tickets filed from this analysis: R3, R4, R6, R7, R8 (proposed, one solo step each). R1, R2 and R5 belong to the docs-schema tickets. R9 and R10 are listed and not filed.

## What not to build

- A capability registry with `discover`, `inspect` and `read` tools [O `04-context-and-harness.md:29-33`]. No contract is used in either repository, and the skill requires "an actual need" [O `PC/SKILL.md:24`]. A registry nobody queries is cost with no reader.
- An ontology or knowledge graph. A kind table does the work, and the skill says a profile is "not a second core ontology" [O `contracts.md:39`].
- A T9 or T4 tier (UI IR, composition grammar, renderer). The A2UI route is optional and no renderer ships [O `a2ui.md:3`].
- Stored lifecycle states or a state machine [O `PC/SKILL.md:24,26`; `evidence.md:25`].
- Semantic retrieval over docs. The proposal itself says to start lexical [O `04-context-and-harness.md:23`], and entry files route by task.
- A prescribed folder tree inside Progressive Context [O `docs/repo-onboarding/design.md:195`]. The layout stays in SDLC Lite.

## Limits of this analysis

- One analyst read the cited files. Documents 01, 05 and 06 of the proposal set were read by heading only; document 03 was read in part.
- The plugin's behavior in a live session was not measured here, only its text.
- Maison was searched with `git grep` over tracked files; its `.sdlc/` is ignored by Git.
- Rubric scores and the 36-point scaling are my inference. No external standard other than the skill's rubric and W3C PROV [O `README.md:45`] is relied on.

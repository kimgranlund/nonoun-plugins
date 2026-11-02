# Changelog

The context plugin (formerly Progressive Context), newest first. Releases before 0.2.0 are recorded only in git history.

## [Unreleased]

### Changed

- `evaluation-system` (T-0838): gold has provenance and gates track the target version. Cases gain `basis` (owner, judgment, convention, agent), `kind` (standard, invariance, negation) and `variant_of`; gates gain `question_id`, a `basis` filter, `min_coverage`, a required `pinned_target_version` and the `stale` status. `run_suite.py` reports coverage, accuracy per direction (a gate fails when either direction is below its threshold), results by basis with an owner row, and calibration (per-band accuracy and ECE on dev) when the target returns `confidence`, and marks a gate `stale` when `--target-version` differs from its pin. `validate_suite.py` adds `missing-variant`, `convention-in-judgment-gate`, `uncalibrated-gate` (`--runs`) and `stale-gate` (`--target-version`) errors and `missing-basis` and `convention-in-judgment-suite` warnings; `missing-basis` stays a warning while `classify-and-resolve`'s `logs_to_cases.py` writes no basis. New `templates/LESSONS.md` ledger. A gate registry without `pinned_target_version` now fails validation.

## [0.6.0] - 2026-11-01

### Added

- `classify-and-resolve` (T-0835): designs and grows classify-and-dispatch workflows (triage, routing, intake, router agents, review queues): a closed class set from a `knowledge-organization-system` scheme with an explicit `unclassified` route, a cascade of rule, model and human steps that abstain rather than guess, resolver contracts whose `side_effects` and `autonomy` follow a matrix guarded by `evaluation-system` gates, and four evidence-gated stages (manual, rules, model, automate). It publishes the Item, Classification, EntityMatch, Resolver, Resolution and Pipeline spine (`references/model.md`) and a JSONL log schema, and ships `scripts/validate_pipeline.py` (unrouted classes, unknown resolvers, unresolved or deprecated route keys, a missing or auto unclassified route, a cascade with no fallthrough, autonomy-matrix violations, unknown or unpassed gates, thresholds outside [0, 1], plus log-volume warnings), `scripts/logs_to_cases.py` (logs to production evaluation cases, split by item-id hash) and `scripts/unclassified_report.py` (deterministic candidate concepts with evidence ids for a KOS change). References cover the model, resolvers and escalation, and growth with a Stage 0 to Stage 1 walkthrough; `evals/trigger-activation.suite.yaml` is its own trigger suite.
- `evaluation-system` (T-0833): decides whether a prompt, agent, classifier, skill trigger or human review process is good enough, using evidence. It owns the Case, Grader, Suite, Run and Gate schemas (`references/model.md`, field names stable for `classify-and-resolve`), grows a suite through four evidence-gated stages (seed, regression, measure, gate), and ships `scripts/validate_suite.py` (duplicate ids, cases without evidence, unknown graders, broken gate references, unvalidated judges backing gates, holdout cases in tuning, expected labels missing from the `knowledge-organization-system` vocabulary) and `scripts/run_suite.py`, which runs any target through a JSON stdin and stdout adapter, reads human outcomes from a results file, and writes `run.json` and `report.md` with per-slice Wilson intervals and gate statuses, `insufficient_n` below `min_n`. References cover the model, graders with a human-agreement procedure, and growth with a Stage 0 to Stage 1 walkthrough; `evals/trigger-activation.suite.yaml` is its own trigger suite.
- `controlled-natural-language` (T-0832): governs sentence patterns in high-stakes docs (requirements, ADRs, runbooks, policies, prompts, research findings) after the STE, EARS and Attempto traditions. A Stage 0 rule set (`templates/rules.yaml`) holds typed-slot patterns for one doc type, four evidence-gated stages (seed, enforce, extend patterns, extend doc types) govern growth, and `scripts/lint_cnl.py` (standard library plus PyYAML) reports retired labels, sentences that fit no pattern, unresolved concept slots, banned words and rules naming missing concepts, resolving slots against the `knowledge-organization-system` vocabulary without defining terms. References cover the rules file and a pattern catalog, growth with a Stage 0 to Stage 1 walkthrough, and trigger tests.
- `knowledge-organization-system` (T-0831): keeps a corpus's vocabulary consistent through a lightweight SKOS model (`templates/vocabulary.yaml`), four evidence-gated growth stages (seed, synonyms, hierarchy, schemes) and `scripts/validate_kos.py` (standard library plus PyYAML), which checks labels, definitions, links, hierarchy cycles, schemes and stage gates and, given `--corpus`, unreferenced concepts and retired-label use. The vocabulary field names are a stable contract for `controlled-natural-language`. References cover the model, growth with a Stage 0 to Stage 1 walkthrough, and trigger tests.

### Changed

- `knowledge-organization-system` and `controlled-natural-language` carry their trigger tests as `evals/trigger-activation.suite.yaml` in the `evaluation-system` suite format (T-0834): the same 10 activating and 5 non-activating prompts, each with `expected`, `added_because` and a `human` grader; `references/trigger-tests.md` is gone from both.

## [0.5.1] - 2026-10-31

### Changed

- `progressive-context` takes the MacBook edits made after the T-0829 import (T-0830), so the skill reads less: start from the task and its authoritative context, open a reference only for an unresolved context mechanism, and treat evaluation, semantic handoff and gap-analysis templates as optional when local checks or formats suffice. `SKILL.md` and the `evaluation`, `semantic-handoff`, `review-rubric` and `tier-model` references change; the SKILL.md line linking the earlier references stays.

## [0.5.0] - 2026-10-31

### Added

- `knowledge-modeling` moves in from the MacBook working copy (T-0828): define and evolve domain concepts, typed relationships, evidence-backed mappings and interpretation rules. Its content is unchanged; `.DS_Store` was left out.

### Changed

- `progressive-context` is replaced by the MacBook rewrite (T-0829): context-system design through traversal, a tier model, a review rubric, semantic handoff to `knowledge-modeling` and route evaluation, with JSON schemas, `scripts/validate.py`, `scripts/replay.py`, tests, templates and a worked corpus. `references/contracts.md` now holds the optional JSON contract; the earlier capability-contract guide moves unchanged to `references/capability-contracts.md`. It and the six references the rewrite drops (`evidence`, `sdlc`, `a2ui`, `browser-harness`, `workflow-stages`, `performance-contract`) stay unchanged and are linked from one SKILL.md line. `.DS_Store` and `__pycache__` were left out.

### Upgrade

- Update the plugin, then remove a hand-copied `knowledge-modeling` from `~/.claude/skills` or `~/.codex/skills` so each host loads one version.

## [0.4.0] - 2026-10-30

### Added

- `context-fog-of-war` gains explicit delivery diagnostics from the MacBook working copy (T-0824): `scripts/delivery.py`, a `--delivery-contract` option in `engineer.py`, delivery keys in `session.schema.json`, two new test files, Claude adapter 1.1.0, scoped read requests and a persisted-output preview in truncation. Project-specific front matter was left out.

### Upgrade

- Update the plugin. A machine that keeps a hand-copied `context-fog-of-war` in `~/.claude/skills` or `~/.codex/skills` should remove it so each host loads one version.

## [0.3.0] - 2026-10-25

### Added

- Five context skills move in from the user-level skill folders (T-0790): `context-fog-of-war`, `context-routing-review`, `generative-systems`, `system-atlas` and `icm-architect`. Their content is unchanged except that links into evidence left out of the package (`generative-systems/resources/reports/`, two design skills' reports, a local download) became code spans. `progressive-context` is unchanged.

### Upgrade

- Update the plugin, then remove the user-level copies of the five skills (`~/.claude/skills/<name>`, `~/.codex/skills/<name>`) so each host loads one version. Start a fresh chat after the change.

## [0.2.0] - 2026-10-25

### Changed

- The plugin is renamed from `progressive-context` to `context` and now lives in `plugins/context/` (T-0793). Its skill keeps the name `progressive-context`, so it is invoked as `/context:progressive-context` in Claude Code and still as `$progressive-context` in Codex. Skill behavior is unchanged.

### Upgrade

- The install id changed. Claude Code: run `/plugin install context@sdlc-lite`, then `/plugin uninstall progressive-context@sdlc-lite` and remove any `progressive-context@sdlc-lite` entry left in `enabledPlugins` in your settings. Codex: refresh the marketplace, enable `context`, and remove `progressive-context`.
- Start a fresh chat after the change.

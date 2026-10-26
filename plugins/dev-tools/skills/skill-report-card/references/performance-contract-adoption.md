# Reproducible skill performance contracts

## Ownership and location

Each measured skill owns `references/performance-contract.json`. Its SKILL.md contains only an evaluation/maintenance pointer; ordinary authoring must not load the metric contract. No README or duplicated KPI prose is needed.

This skill owns the format: [schema v1](performance-contract.schema.json), a [proposed base-ui example](../assets/performance-contract.example.json) and `scripts/validate_contract.py`. The validator is a stdlib implementation of the schema vocabulary used here, not a general JSON Schema engine. It fails on unknown schema keywords; extend it or use a qualified Draft 2020-12 validator if the schema expands.

- Measured skill: goals, metric meaning, applicability, conceptual boundaries.
- skill-report-card: evidence adapters, qualification and calculation implementation.
- Evaluation protocol: cohort, environments, targets chosen before results, attempt/repair rules.
- Report snapshot: observations, calculated values, source identities and limitations.

Default targets may be null. Non-null defaults require rationale and declared scope; a protocol target is separately attributed, never silently written back to the skill. Operational measurements and current scores are forbidden fields in the definition contract.

## Adoption procedure

1. Confirm authorization to edit the target skill. Read its SKILL.md and the relevant capability contracts, not entire historical reports. Identify the intended outcome and ownership boundaries.
2. Inventory any existing performance contract and registry definition. Reconcile conflicts explicitly; do not create a second editable authority. Keep stable metric IDs when meaning is unchanged.
3. Draft exactly one primary goal plus secondary goals with stable IDs. Define 3-8 KPIs, each linked to defined goals. At least one must address the primary goal.
4. For each KPI, fill its measurement type, unit, direction, applicability, exclusions, required evidence, cohort dimensions and missing-data rule. Specify what it excludes conceptually in boundary. Use a ratio for counts, a distribution for measured costs, or a declared rubric for judgment; never label a rubric an objective rate without scoring rules.
5. Human/maintainer review: every dimension answers a distinct question. Check double-counting, incentives, quality/cost conflicts and dependency overlap. Structural validation cannot perform this review. Do not invent targets to make a dashboard look complete.
6. Save the proposed contract at `TARGET_SKILL/references/performance-contract.json`. Start at contractVersion 1.0.0; schemaVersion is 1. Preserve a prior contract before replacing it.
7. Run `python3 REPORT_CARD_ROOT/scripts/validate_contract.py TARGET_SKILL/references/performance-contract.json`. It returns only identity/count/hash or a structural error. Require positive and relevant negative controls for any schema/validator change.
8. After the definitions are agreed, set status to adopted and add this short pointer to the target's SKILL.md:

   `Goals and measurement definitions: [performance contract](references/performance-contract.json). Read when evaluating or changing intended outcomes; ordinary authoring does not require it.`

9. Record adoption evidence: target path, contract version, exact SHA-256, review decisions and affected checks. If the target skill has a seal/package workflow, follow it. Do not automatically run a new efficacy study.
10. Reconcile the central proposal registry only when all affected consumers support skill-owned contracts. Replace the duplicate definition with a discovery reference, preserving the former proposal snapshot. Never delete the current registry before updating its scanner/renderer consumers.

## Versioning and historical interpretation

schemaVersion changes when contract shape changes incompatibly. contractVersion changes when a skill's definitions change: major for changed meaning, population, unit or scoring; minor for additive compatible metrics/goals; patch for wording changes that do not affect interpretation. Retired metrics must not have their IDs reassigned to different meanings.

Report snapshots must preserve the exact contract bytes/hash, schemaVersion, contractVersion, skill identity and adapter version used. Historical reports retain their original interpretation. A recalculation under a new definition is a separately labelled reanalysis, not a rewrite or a new author attempt. A hash records correspondence, not agreement or trust.

## Future contract discovery (not yet wired into collection)

Look for the exact path beneath an identified skill installation. Apply normal size, symlink and exclusion controls. Validate structure and goal references before using it. An adopted skill-owned contract is the authority for that skill/version; proposed contracts remain visibly proposed. Multiple incompatible installations or contracts are separate identities or a conflict, never an arbitrary first-match choice.

Until discovery is implemented, references/kpis.json remains the working proposal registry. The supplied example demonstrates the schema but does not adopt goals into base-ui. All KPI values remain unmeasured; adopting a definition does not provide evidence.

## Acceptance checklist

- [ ] Target skill is authorized and existing definitions reconciled.
- [ ] Exactly one primary goal; 3-8 distinct KPIs; valid goal links.
- [ ] Evidence and eligibility can support each denominator/rubric.
- [ ] Targets are null or justified; quality constraints guard efficiency metrics.
- [ ] No dependency double-counting or conflicting incentives.
- [ ] Validator passes; relevant rejection controls pass.
- [ ] Definition version/hash and review decision recorded.
- [ ] SKILL.md has a small optional pointer, no metric dump.
- [ ] Registry consumers migrated before duplicate authority removal.
- [ ] Historical reports/limitations preserved; publication remains explicitly scoped.

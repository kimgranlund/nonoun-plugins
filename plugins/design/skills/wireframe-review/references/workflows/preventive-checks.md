# Preventive artifact checks

The standard `generate.mjs` entry point runs artifact lint automatically and blocks publication on errors. Use the standalone lint command below for independently authored HTML or diagnosis, before expensive interaction checks. These checks inspect initial parsed documents. They do not execute application scripts or certify behavior/accessibility.

## Artifact lint

`node scripts/lint-artifact.mjs HTML_OR_MANIFEST PLAYWRIGHT NEW_REPORT [POLICY_JSON]`

A manifest input goes through the real builder first. HTML is parsed using Chromium's DOM parser; style declarations use CSSOM. Input scripts never execute and network requests are blocked. Each inline frame is inspected as a separate document. Templates remain inert; shadow roots, non-inline frames, linked styles and runtime states require separate checks. The report includes input, inspected HTML, rule-source and optional policy hashes.

Errors: duplicate DOM IDs, empty or missing label/ARIA/popover references, non-labelable native label targets and popover targets without `popover`. Custom-element labelability remains unverified. Multi-ID ARIA references are resolved individually. An existing reference is not proof of an accessible name or successful interaction.

Warnings: explicit length overrides of owned component padding/gap/radius, and inline child margins inside known gap-owning compositions. Ownership classes come from the component contract. These are advisory candidates, not computed-cascade findings; conditional selectors may not apply in the current environment. Exact source-owned reset rules are recognized from installed stylesheet bytes; authored zero-length overrides remain inspectable. Token-based values are allowed. Custom geometry owners produce unverified coverage, not a clean fidelity score. Do not globally ban numeric literals. Do not promote these rules to errors without checking realistic allowed cases.

A genuinely dynamic target can be deferred with a narrow policy:

```json
{
  "deferredReferences": [{
    "document": "root",
    "selector": "#open-editor",
    "attribute": "aria-controls",
    "target": "editor-panel",
    "reason": "Panel is created when editing begins",
    "state": "editing"
  }]
}
```

Nested document keys are `root/iframe[0]`, recursively. A matched deferral produces an **unverified** finding requiring a later state check, never a pass. An unused deferral fails so exceptions cannot silently accumulate. Nonzero exit indicates errors; zero can still include warnings and unverified coverage. Inspect the report before making a delivery claim.

## Selecting existing checks

`node scripts/select-checks.mjs SKILL_RELATIVE_CHANGED_PATH...`

This prints suggested commands and reasons, grouped by stage. It never runs them. [Conditional build checks](build-checks.md) remains authoritative. Unmapped changes require manual routing; foundation/recipe changes also require selecting their affected behavior checks. The selector is intentionally not a complete dependency graph.

Optional `--reuse RECORD_JSON ENVIRONMENT_ID` assesses reuse eligibility for an existing observation. The record must have `status: "pass"`, a nonempty `scope`, matching `environment`, and `dependencies` with absolute `path`, `sha256`, and `kind` fields. Include at least one `source` and one `fixture`; include every relevant transitive source, fixture and driver. A report hash alone is rejected. Any changed dependency or environment rejects reuse. Eligibility applies only to the declared scope; the caller must review dependency completeness. It does not mutate or upgrade old evidence.

## Maintaining these checks

Run `node scripts/check-preventive-lint.mjs PLAYWRIGHT` after changing rules or routing. It exercises the actual lint CLI, valid and broken documents, frame isolation, deferred targets, advisory style cases, a built manifest fault, and selector/evidence-reuse controls. Output goes to a fresh temporary directory. Keep this focused; no generation round or broad browser suite follows automatically.

Native checkbox/radio inputs inside recognized product compositions warn when maintained mark classes are missing (switch anatomy is separate). This does not certify all component anatomy. Source-owned reset matching uses parsed complete rules; it does not suppress arbitrary authored overrides or treat all zero values as trusted.

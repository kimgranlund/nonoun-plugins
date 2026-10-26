# Generation, context and delivery publication

Implemented the bounded peer specification, preserving existing generation/lint/static gates and the independent acceptance runner. No third browser runner or lint framework was added.

## Supported delivery and authoring paths

- Draft: `node scripts/generate.mjs MANIFEST NEW_OUTPUT PLAYWRIGHT [--controller JS]`. Emission reports compile/structural/startup/lint results and delivery-incomplete when no evaluator task acceptance is supplied.
- Scoped delivery: add `--acceptance EVALUATOR_JSON`. The existing verify-acceptance runner executes against the exact final compiled artifact before promotion. Required failures/unsupported/unexecuted coverage retain diagnostic artifact/report and do not publish a delivery-verified output. Source/controller/criteria and artifact/runner/check identities are recorded; paths are rewritten after stage promotion.
- Existing evidence identity: `node scripts/verify-acceptance.mjs --check-report REPORT HTML ACCEPTANCE`. Changed artifact/criteria/runner/check bytes reject reuse. Identity does not prove evaluator independence or completeness.
- Source seam: `node scripts/authoring-starter.mjs NEW_SOURCE_DIR PROJECT_ID LEAF_ID`; edit unit.html and metadata, run emitted assemble.mjs, then generation. JSON serialization keeps quotes/backslashes and leaf composition valid. Existing sources cannot be overwritten. Multiple variants/pages still require their own composition contract.
- Assets: `node scripts/authoring-starter.mjs --icons` lists exact offline bundled names. No guessed glyph download, aliases or silent replacement.
- Supplied APIs: `node scripts/component-context.mjs --runtime` returns the authoritative prototype-api.json with source hashes, names/signatures, lexical controller scope, prerequisites, timing, returns/failures and limits. Ordinary family retrieval does not load this declaration. Catalog-local helpers are not implied APIs.

## Acceptance version 2

Version 1 remains supported with shared per-case state. Version 2 starts each requirement/scenario in a fresh page/route, with explicit setup and caseIds. Focus assertions inspect the actual owner document. Owned remount replaces the preview even when the requested viewport already matches. Prerequisites name earlier requirements; failed prerequisites are blocked. Not-applicable cases, unexecuted requirements, unsupported routes/compositing, setup/binding errors, assertion failures and application exceptions remain distinct. Unknown application exceptions are never suppressed. Draft versus final-save policy belongs to evaluator criteria; valid Save/Restore setup fills all required fields and edits every saved field before restoring.

The generator's author interaction list cannot erase evaluator requirements. Criteria must be authored/frozen from the brief outside generator-writable output; copying/hashing does not enforce ownership or prove completeness. Accepted environment limitations remain separate explicit user decisions, not passes or waivers for failures.

## Discriminating pilot evidence

| Peer criterion | Qualified result / evidence |
| --- | --- |
| 1. Valid staged task | pilot-final/baseline.json passes staged focus, typing/remount, validation, Save/Restore and search. |
| 2. Activation-only missing helper | pilot-final/missing-helper.json: application-exception on activation despite successful startup. |
| 3. Omitted focus | pilot-final/omitted-focus.json: assertion-failure without needing an exception. |
| 4. Independent scenarios after failure | Same report: Save/Restore and revised search pass from fresh setup despite failed focus. |
| 5. Omitted author interactions | Pilot manifest has no interactions; evaluator focus/search/save requirements still execute and can fail. |
| 6. Absent revised-search target | pilot-final/missing-search-target.json: actual input callback exception; not a JavaScript free-variable regex. |
| 7. Draft/final policy | pilot-final/baseline.json tests invalid final save; pilot-final/draft-policy.json permits incomplete draft under its own criteria. |
| 8. Unsupported/unexecuted coverage | pilot-final/unsupported-proposal.json and unexecuted.json prevent verified delivery; unsupported-compositing/report.json records unsupported. |
| 9. Stale artifact/check identity | Pilot and final replay reject changed artifact/check identity; fresh baseline identity is accepted. |
| 10. Actual proposal coverage | rendered.json.evidence.json has four viewport/scheme combinations for one A proposal, not twelve manufactured A/B/C combinations. |

The pilot-final/delivered generation receipt confirms the real --acceptance path and valid promoted report paths. Failed delivery remains only in retained stage diagnostics. Existing version-1 baseline plus nine negative mutations pass in legacy-final. Eight generation pipeline paths pass in pipeline-verification. Source-authoring/API controls pass in authoring-check; exact family/shared/batched/runtime lookup and growth/guard controls pass in context-final. Syntax, corpus graph, skill validation, token-index identity and exact 53-item register checks pass.

## Qualifications and remaining uncertainty

The bounded component-context test originally requested repeated full shared+family payloads and exceeded its reader budget. It now checks the documented record-only/shared-once route, preserving exact declarations and the original failures; the budget was not raised. Runtime API detail was moved behind its dedicated route instead of bloating all family reads.

Pipeline testing revealed startup selected hidden View before selecting a page in an all-pages artifact. The page is now selected first; affected pipeline checks pass. Earlier failed attempt is retained in session evidence. No component focus implementation was rebuilt, and its prior matrices remain reusable.

Focused fixtures establish integration/predicate behavior, not fresh model adoption, evaluator completeness, perceptual hierarchy, complete accessibility or native environment parity. No generation tournament ran. Previous WebKit ResizeObserver notifications remain unresolved; this acceptance runner does not suppress them. The 53/53 register, accepted limitations, sealed holdout, historical evidence and peer-owned live components.html remain preserved. Canonical sheets and ZIP are synchronized; preceding canonical/archive retained.

Exact changed files: changed-files.json. Sources and commands are in this evidence directory, with reusable focused checks in the installed skill. Main retains integration/publication ownership; no new peer file reservation is assigned.

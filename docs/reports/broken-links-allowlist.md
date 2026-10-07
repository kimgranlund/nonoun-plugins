# Broken-link allowlist

Links that stay unresolved on purpose. `scripts/check.py` item 32 fails when a tracked Markdown file holds a broken relative link that is not listed here, or when a row here no longer matches a broken link. Entries are code spans so this file adds no links of its own.

| File | Target | Why it stays |
|---|---|---|
| `.sdlc/.0185-evals-folder/planner-L3.md` | `../.sdlc/evals/AGENTS.md` | Dated text quoting a line meant for another file; resolves from that file, not this one |
| `.sdlc/.0185-evals-folder/step-4/handoff.md` | `../../.sdlc/evals/AGENTS.md` | Same: quoted text addressed to another file |
| `.sdlc/.0185-evals-folder/step-4/handoff.md` | `../.sdlc/evals/AGENTS.md` | Same: quoted text addressed to another file |
| `.sdlc/verify-0227-b/verifier-L3.md` | `validation/solo-vs-lean-benchmark-2026-10-04.md` | Frozen record of a command that ran before the rename to reports |
| `.sdlc/verify-0227-b/verifier-L3.md` | `design.md` | Bare name relative to the ticket it described |
| `.sdlc/verify-0227/verifier-L3.md` | `README.md` | Bare name relative to the ticket it described |
| `.sdlc/verify-docs-schema-2/verifier-L3.md` | `../validation/docs-schema-design-review.md` | Quoted text addressed to a file in another folder; frozen record |
| `.sdlc/verify-docs-schema-3/verifier-L3.md` | `../validation/docs-schema-design-review.md` | Same |
| `docs/specs/generative-constructs/README.md` | `../../../../gen-ui-system-svelte-lite/docs/references/folder-native-gen-ui-ontology.md` | Sibling repository, not tracked here |
| `docs/specs/generative-constructs/progressive-context-plugin.md` | `../../../../gen-ui-system-svelte-lite/docs/references/folder-native-gen-ui-ontology.md` | Sibling repository, not tracked here |
| `docs/reports/reorg-inventory-live-run.md` | `contract.json` | File of the throwaway maison project the run inspected |
| `docs/reports/reorg-inventory-live-run/maison-plan.md` | `component.md` | File of the throwaway maison project the run inspected |

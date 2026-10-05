# Broken-link allowlist

Links that stay unresolved on purpose. `scripts/check.py` item 32 fails when a tracked Markdown file holds a broken relative link that is not listed here, or when a row here no longer matches a broken link. Entries are code spans so this file adds no links of its own.

| File | Target | Why it stays |
|---|---|---|
| `.sdlc/.0181-messages-wait/planner-L3-2.md` | `validation/messages-wait-live-run.md` | Dated plan quoting a README line written before the move to reports |
| `.sdlc/.0181-messages-wait/step-4/handoff.md` | `validation/messages-wait-live-run.md` | Same quoted README line in a frozen handoff |
| `.sdlc/verify-0227-b/verifier-L3.md` | `design.md` | Bare name relative to the ticket it described, not this folder |
| `.sdlc/verify-0227/verifier-L3.md` | `README.md` | Bare name relative to the ticket it described, not this folder |
| `docs/generative-constructs/README.md` | `../../../gen-ui-system-svelte-lite/docs/references/folder-native-gen-ui-ontology.md` | Sibling repository, not tracked here |
| `docs/generative-constructs/progressive-context-plugin.md` | `../../../gen-ui-system-svelte-lite/docs/references/folder-native-gen-ui-ontology.md` | Sibling repository, not tracked here |
| `docs/reports/reorg-inventory-live-run.md` | `contract.json` | File of the throwaway maison project the run inspected |
| `docs/reports/reorg-inventory-live-run/maison-plan.md` | `component.md` | File of the throwaway maison project the run inspected |

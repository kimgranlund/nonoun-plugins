# Base UI dependency

Install base-ui and wireframe-review as siblings. Generation/build accepts --ui-kit ROOT (or WIREFRAME_UI_KIT for subprocess checks), otherwise resolves ../base-ui. The trusted kit must match ui-kit.lock.json. Missing dependency, incompatible API or changed bytes stops generation before output. No network installation or stale fallback is used.

UI CSS, tokens, components, recipes and pure sheet renderers are owned by base-ui. ui-compatibility.json lists generated copies retained for historical paths and integration checks. After an intentional UI update: run affected checks in base-ui, seal its descriptor, then node scripts/sync-ui-kit.mjs and node scripts/sync-ui-kit.mjs --check. Do not run sync against an unreviewed kit; it intentionally updates the lock and copies. Do not edit generated copies.

The review build embeds the kit and assets/review-runtime-adapter.js. assets/prototype-runtime.js is a generated compatibility concatenation for old harnesses. registerPrototype, approval helpers, unit/variant keys, read-only host policy and feedback belong to the review tool. Generic state/render/bind, cleanup and heading focus belong to base-ui. Existing controllers keep their API.

component-context.mjs uses base-ui contracts by default; --runtime retains the review adapter contract. Explicit --root retains the previous corpus lookup for frozen evaluation fixtures. It does not change the kit used for building. Generic runtime callers use the base-ui entry.

Current sheets keep their canonical destination and deep links. Catalog collection and UI renderers are direct locked-kit API calls; the page shell and ledger/history remain review-owned. Generated source-path views remain for legacy readers. Peer-owned live sheets are not a migration output. Release archives include generated compatibility copies for legacy readers but generation requires the sibling kit. Extract both archives into the same parent. No symlink or machine-specific absolute path is required.

Rollback uses the archived compatible skill pair; never restore one side alone. Accepted limitations and historical evidence keep their original meaning. Old independently frozen evaluation scripts may require their original corpus, never overwrite it to make checks pass.


## UI checks

Standalone UI checks now live in base-ui; references/checks.json there indexes the commands. Existing review-tool command paths forward through scripts/run-ui-check.mjs, preserving arguments, stdout and exit status. Use --describe-route on a forwarding command to inspect its target. scripts/check-ui-check-routing.mjs verifies routing without rerunning all component matrices. Shell icon generation now uses the kit API and replaces the glyph block in place. Review artifacts, controller adapters, sheets and historical-evidence checks remain owned here.

For later removals, follow [compatibility retirement](migration/compatibility-retirement.md). A text-search miss is not proof that a compatibility path is unused.

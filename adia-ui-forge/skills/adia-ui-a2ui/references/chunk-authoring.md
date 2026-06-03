# Reference: Chunk authoring — HTML-first synthesis + harvest

**Source:** Absorbed from the former `a2ui-pipeline` skill §Training Data Flow (Phase 3 rollup). **Used by:** mode 3 of `adia-ui-a2ui` (author or refine a chunk). **Companion:** `corpus-discipline.md`, `fragment-graph.md`.

---

## Training Data Flow

Use when adding a new component, expanding an existing one, or debugging why the generator isn't picking up a variant.

### The 4 training signals (all register into one pattern library)

1. **Hand-authored monolithic patterns** — `packages/a2ui/compose/patterns/<domain>/<name>.json`
   - Full-page templates, optional `wiring` block
   - Loaded by `pattern-library.js::_loadNode()` walking domain dirs
   - Top of retrieval priority; highest-leverage signal

2. **Zettel fragments + compositions** — `packages/a2ui/compose/{fragments,compositions}/`
   - Fragments = atomic reusable subtrees with typed slots
   - Compositions = larger patterns that reference fragments via `$fragment`
   - Loaded by the zettel engine, resolved by `composer.js::resolveComposition()`
   - Preferred for anything with ≥3 leverage (see `fragment-graph.md` — the leverage rule)

3. **Component `.a2ui.json` examples** — `packages/web-components/components/<name>/<name>.a2ui.json`
   - Each component has an `examples[]` array of variant templates
   - Registered automatically at load by `pattern-library.js::_processA2UIData()`
   - Best home for per-component variant coverage

4. **Training-extracted pages + chunks** — `packages/a2ui/compose/training/{pages,chunks}/*.json`
   - Auto-extracted from `packages/web-components/catalog/training/ui/*/index.html`
   - Decomposed into card-level/section-level chunks by `training/extract.js`
   - Ingested via `training/ingest.js` at test time (or programmatically)

## Authoring order for a new component

Do these in sequence; each feeds the next:

1. **Source** — `packages/web-components/components/<name>/{js,css,a2ui.json,yaml}`
   - `<name>.yaml` for narrative (scaffold via `npm run yaml:scaffold`)
2. **Demo fragment** — `packages/web-components/components/<name>/<name>.examples.html` (and standalone shell `<name>.html`; optional `<name>.examples.js` controller — see `docs/conventions/composition-and-examples.md` and ADR-0020)
   - One `<section data-section data-property="<variant>">` per variant
   - `<p data-note>` describes the variant (this becomes the example description)
3. **Sitemap entry** — `site/sitemap.json` Components section, inserted alphabetically
4. **A2UI examples** — for each demo variant, add an entry to `<name>.a2ui.json`'s `examples[]` array with:
   - `name`: slug matching the demo's `data-property`
   - `description`: pulled from `<p data-note>` text, keyword-rich
   - `template`: A2UI JSON tree using PascalCase component names (`Chat`, not `chat-ui`)
5. **Verify** — `npm run test:a2ui` (check post-ingest pattern count went up)

## Canonical source for variants

**Demo fragments at `packages/web-components/components/<name>/<name>.examples.html` are authoritative.**

The `<section data-section>` blocks define what variants exist. The `.a2ui.json` examples should mirror them 1:1. If they drift, the demo page wins — update the examples to match, not the other way around.

Rationale: demo pages are live-rendering, human-verified, and alphabetically auditable via the sitemap. JSON examples are machine-readable but invisible to manual QA.

## Path quirks (post-package-reorg)

- `extract.js` resolves `TRAINING_DIR` via `join(__dirname, '..', '..', 'web-components', 'catalog', 'training')`. An earlier path bug resolved it to `packages/training-data/` (non-existent) and silently extracted 0 pages, 0 chunks. **Always run the tool directly after migrations** — unit tests passed despite the breakage because they exercise downstream artifacts, not extraction.
- Training data lives in `packages/web-components/catalog/training/{ui,prose}/`, NOT at repo root or in a `training-data/` dir.

## Scale notes (corpus baseline)

- ~100 monolithic patterns
- ~71 compositions + ~26 fragments
- ~520 post-ingest pattern count (includes component examples + extracted training pages/chunks)
- Baseline zettel coverage 100% @ avgScore ~89; mono 100% @ avgScore ~97
- Reuse ratio ~29.9%

These are order-of-magnitude reference points, not gate values — the live gate thresholds are in SKILL.md §Plan-Execute-Verify and the eval baseline at `scripts/eval-baseline.json`.

## Quick audit — is a variant actually trained?

After authoring a new variant:

```bash
node scripts/build/components.mjs
node packages/a2ui/corpus/scripts/extract.js
npm run test:a2ui    # check "Post-ingest count"
```

If the count didn't increase, the variant isn't flowing through. Check:

1. Is the example in `<name>.a2ui.json`'s `examples[]` array?
2. Does the template use PascalCase component names?
3. Does it have a unique `name` slug?
4. Does `registerPattern()` accept the template? (look for `pattern.name && Array.isArray(pattern.template)` checks)

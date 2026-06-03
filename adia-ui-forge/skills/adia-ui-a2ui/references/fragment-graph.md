# Reference: Fragment graph — leverage rule, extraction, $fragment refs

**Source:** Absorbed from the former `a2ui-pipeline` skill (§Fragment Extraction) and `zettel-internals` (§How fragment-graph composer resolves `$fragment` refs) — Phase 3 rollup. **Used by:** mode 4 of `adia-ui-a2ui` (extract a fragment). **Companion:** `strategy-engines.md`, `chunk-authoring.md`.

---

## Fragment Extraction

Use when converting a monolithic pattern into a composition that references one or more zettel fragments, OR when authoring a new fragment from shared substructure across multiple patterns.

## The leverage rule

**Do not extract a fragment unless it has leverage ≥ 3** — i.e., at least 3 compositions would use it. Two exceptions:

1. Singleton fragment that closes a well-defined semantic gap (e.g., `kbd-shortcut-row` even at leverage 1, because "a keyboard shortcut row" is a distinct domain primitive).

2. **Intra-composition multi-use.** A single composition that instantiates the same fragment N times (N ≥ ~10) also justifies extraction — reuse ratio is `fragment_refs / composition_nodes`, not `fragments / comps`. Example: `calendar-day-cell` is used 35× inside one composition (`calendar-month-view`), and this alone lifted corpus reuse from 26.4% → 33.5%. Treat a repeating subtree of 10+ instances as a fragment even if no other composition references it yet.

Sub-leverage fragments bloat the library, slow retrieval, and make maintenance harder without improving reuse.

## Steps

1. **Candidate identification**
   - Look for repeated subtrees across ≥ 3 patterns
   - Common candidates: card headers, key-value rows, icon+text rows, labeled progress bars, stat displays, notification rows
   - Check for existing fragment first: `ls packages/a2ui/compose/fragments/` or call the `zettel_stats` MCP tool to see the current corpus

2. **Fragment authoring**
   - File: `packages/a2ui/compose/fragments/<name>.json`
   - Schema: `{ name, description, keywords, slots, template }`
   - Keywords should be rich — retrieval depends on them
   - Slots use `{ $slot: 'name' }` placeholders in the template

3. **Composition refactor**
   - Replace the inlined subtree with `{ $fragment: 'name', bindings: {...} }`
   - Composer at `packages/a2ui/compose/strategies/zettel/composer.js` handles namespaced id rewriting and slot expansion

4. **KEYWORD PRESERVATION (critical)**
   - Extraction SHRINKS the composition's own keyword surface
   - Before: the composition contained all the subtree's text
   - After: the composition only references the fragment
   - **Fix:** enrich the composition's `keywords` field with the semantic tokens that left with the fragment
   - Without this, retrieval degrades silently

5. **Rebuild + verify**
   - `node scripts/build/components.mjs`
   - Run the full structural-gate sweep (see SKILL.md §Plan-Execute-Verify)
   - Specifically check `eval:diff --engine zettel` for coverage + avgScore regressions

## The extraction drift lesson

During the zettel migration, extracting `card-header-with-description` from the `login-form` pattern dropped its retrieval score from 28 → 24. The cause: the composition lost all the "login", "sign in", "email password" tokens because those moved into the fragment slot bindings.

Fix applied: added `keywords: ["login", "sign in", "email", "password", "authenticate"]` explicitly to the composition. Retrieval rebounded to 28.

**Lesson:** every fragment-using composition must have richer keywords than its inlined predecessor.

## Threshold calibration

If a known-good intent starts scoring below the retrieval threshold after extraction, DO NOT lower the threshold first. First:

1. Verify the composition's keywords were preserved
2. Check the fragment's description doesn't cannibalize the composition's semantic space
3. Only then consider threshold adjustment (current: 22; lowering below 20 starts producing false matches)

## Current corpus state

For the live fragment count, reuse ratio, and top-leverage fragments, run the `zettel_stats` MCP tool or `npm run pipeline:stats` — these are runtime-derived, not pinned in this reference (the numbers drift as the corpus grows).

---

## How fragment-graph composer resolves `$fragment` refs

`composer.js` algorithm (memorize before modifying):

```text
For each node in the composition template:
  If node.$fragment:
    1. Clone the fragment's template
    2. Prefix every internal id with the composition-node id (avoid collisions)
       e.g. fragment node "fi-in" under composition node "email" → "email--fi-in"
    3. Apply slot bindings (set the attribute on the slot's targetId)
       slots: [{ name: "label", targetId: "fi-field", attribute: "label", required: true }]
       bindings: { label: "Email" } → cloned[0].label = "Email"
    4. If node.children was provided, append those ids to the fragment root's children
    5. Emit the fragment root under node.id, then the rest of the fragment nodes
  Else:
    Emit the node as-is
```

**Don't change ID prefixing without a corpus-wide search** — fragments that compose nest IDs predictably; consumers may pattern-match on the `{compNode}--{fragNode}` shape.

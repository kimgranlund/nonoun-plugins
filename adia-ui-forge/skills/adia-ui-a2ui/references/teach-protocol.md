# Reference: Teach Protocol — Absorbing new knowledge into the adia-ui-a2ui skill

**Why authored:** As the A2UI pipeline absorbs new strategies, anti-patterns, calibration constants, MCP tools, and chunk-corpus shapes, each absorption was previously a one-off improvisation. This protocol gives every future "make sure `adia-ui-a2ui` knows about [pattern]" request a deterministic landing path.

**Decision tree is mechanized.** The branch routing below is authoritative in `scripts/teach-route.mjs` (run `node scripts/teach-route.mjs "<payload>"`). The prose here is for human readers — worked examples, anti-patterns, rationale. The script is the routing.

**Used by:** the `adia-ui-a2ui` skill, when an agent receives one of these triggers:

- "make sure `adia-ui-a2ui` knows about [the new strategy / calibration / anti-pattern]"
- "train `adia-ui-a2ui` on [the new MCP tool / fragment shape / eval finding]"
- "the skill should know about [the new pattern]"
- "absorb this lesson into adia-ui-a2ui"
- "teach the skill about [the new chunk metadata field]"

**Companion:** `eval-diagnostics.md` (run after any pipeline change), `strategy-engines.md` (when the new knowledge is engine-level), and `scripts/audit-a2ui-roster.mjs` (run after any §Teach landing).

**Anti-companion:** `docs/journal/` (arc-specific stories belong in the journal, not the skill — see decision tree Branch H).

---

## When to Use

Trigger phrases (from the §Teach section in SKILL.md):

- "make sure `adia-ui-a2ui` knows about X"
- "train the skill on X"
- "teach the skill about Y"
- "the skill should be aware of Z"
- "absorb [pattern/lesson/feedback] into adia-ui-a2ui"
- "update the skill to reflect [the new strategy / the new threshold / the new tool]"

The phrases are universal across all extensible skills; the **landing target** is what's specific to this skill.

## Core Principles

### 1. The skill is a CITATION layer, not a KNOWLEDGE layer

Per-strategy facts live in `packages/a2ui/compose/strategies/*/`. Chunk authoring rules live in `packages/a2ui/corpus/CHUNK-AUTHORING.md`. MCP tool schemas live in `packages/a2ui/mcp/server.js`. The skill cites by path; it does NOT duplicate code or schema in prose.

**Rule of thumb:** if you catch yourself writing "the zettel composer does X" in a SKILL.md file, stop. Is that fact in the strategy code already? If yes, cite the path + function name + line range. If no, the fact should land in the substrate first, THEN the skill cites it.

### 2. Trigger surface is universal; landing targets are skill-specific

The activation phrases — "train X on Y", "make sure X knows about Z", "absorb this into X" — are the same regardless of which skill X is. The **landing targets** vary per this skill's references/ topology.

### 3. The negative case (Branch H) is load-bearing

Arc-specific stories ("how I debugged this eval regression last month") belong in `docs/journal/`, not in the skill. The skill is procedural knowledge that will be true tomorrow; arc stories are history that's already finished.

### 4. Eval is the source of truth

When a §Teach landing introduces a calibration tweak or new strategy, the eval gate must agree. If the eval gate disagrees with the landing's intuition, the eval gate wins. Rebaseline if the eval threshold itself is wrong; document in CHANGELOG.

### 5. The 5-step landing procedure generalizes

Step 2 (author) is skill-specific. The other four steps are universal across all extensible skills.

### 6. Anti-patterns are universal

The seven anti-patterns generalize across every roll-up: append-only landing, substrate duplication, orphan triggers, capability menu lies, MINOR + PATCH bundling, hygiene-debt deferral, one-way thinking.

---

## The Decision Tree — where does new knowledge land?

Eight branches, each with a worked example. Branch A is the most common landing for substrate-author work; branch H is the negative case (do NOT land in the skill).

### Branch A — New chunk metadata field

**When**: someone adds a new field to chunk JSON (`provenance`, `last_harvested`, etc.) or extends `_index.json` shape.

**Lands at**: `packages/a2ui/corpus/chunks/_index.json` schema documentation in `chunk-authoring.md`. NOT in the skill itself unless the field changes the authoring procedure.

**Worked example**: a `derivation` field was added to chunks recording which HTML demo a chunk was harvested from. Landing: `chunk-authoring.md` got a new section under "Chunk schema" documenting `derivation`. The skill's SKILL.md didn't change.

### Branch B — New MCP tool

**When**: a new tool is exported from `packages/a2ui/mcp/server.js` (e.g., a new `inspect_chunk_keywords` tool joining `search_chunks` + `validate_schema` + `generate_ui`).

**Lands at**: `packages/a2ui/mcp/server.js` (tool implementation) + `mcp-tool-reference.md` (schema doc) + `mcp-pipeline-ops.md` (workflow integration). SKILL.md gets a one-line mention in mode 1's trigger phrases if the tool is operator-facing.

**Worked example**: the `report_issue` MCP tool was added for evolution-engine feedback. Landing was three-fold: server.js implementation + tool-reference schema + pipeline-workflows feedback-loop section.

### Branch C — New strategy / engine

**When**: a new composition strategy is added (e.g., a future `template-match` engine joining `zettel` + `free-form` + `monolithic` + `dogfood`).

**Lands at**: `packages/a2ui/compose/strategies/<name>/` (engine code) + `packages/a2ui/compose/strategies/registry.js` (registration) + `strategy-engines.md` (engine map updated to include the new label). SKILL.md mode 5's trigger phrases may need to mention the new strategy by name.

**Worked example**: the free-form engine was added in a major arc. Landing: new directory under strategies/ + registry.js update + strategy-engines.md got a new section + eval gate added a new threshold row (`cov≥90, avg≥83, F1≥55`).

### Branch D — New anti-pattern rule

**When**: a new anti-pattern is discovered (e.g., "popover-ui without trigger-element rule" joining the existing catalogue).

**Lands at**: `anti-patterns.md` (catalogue entry) + possibly `packages/a2ui/validator/checks/<name>.js` (mechanized check). SKILL.md may need mode 8's trigger phrases extended.

**Worked example**: a "chart-legend-without-tokens" anti-pattern was added during a cross-surface QA arc. Landing: anti-patterns.md got a new rule + validator gained a new check + the sibling `adia-ui-dogfood` skill cross-referenced it.

### Branch E — New calibration constant / threshold

**When**: someone tunes `STRONG_MATCH_THRESHOLD`, `STRONG_RETRIEVAL_SCORE`, the locator weights, or any of the constants in the calibration history.

**Lands at**: `packages/a2ui/compose/strategies/zettel/composer.js` (constant value) + `zettel-calibration.md` (history table — append, never overwrite). SKILL.md doesn't change.

**Worked example**: `STRONG_MATCH_THRESHOLD` was tuned across several arcs. Each tune left a row in `zettel-calibration.md`'s history table with rationale + eval delta. The history is the audit trail.

### Branch F — Methodology / pipeline-design posture

**When**: a new principle / posture emerges that shifts how the pipeline is approached (e.g., "always re-harvest chunks after @bp changes" became a posture during a responsive arc).

**Lands at**: inline in SKILL.md (§Posture or §FirstPrinciples). This is the only branch that touches SKILL.md directly. MINOR version bump.

**Worked example**: the "HTML-first chunk authoring" principle (don't hand-author JSON) was added to §Posture during a training-signal arc.

### Branch G — New fragment-graph node type

**When**: someone extends the fragment graph with a new node type (e.g., adding a `partial` node alongside `fragment` + `composition`).

**Lands at**: `packages/a2ui/compose/strategies/zettel/composer.js` (`$fragment` ref resolution) + `fragment-graph.md` (extended node-type table) + `strategy-engines.md` (how the engine consumes the new type).

**Worked example**: no new node types have been added since the initial fragment-graph design. When one is, the landing pattern follows the existing `$fragment` documentation in fragment-graph.md.

### Branch H (NEGATIVE) — One-off eval debugging arc

**When**: someone debugged a specific eval regression on a specific date. The story has a beginning

- middle + end and won't repeat.

**Lands at**: `docs/journal/` as a dated section. **NOT IN THE SKILL.**

**Worked example**: a chunk-corpus expansion arc (28 → 64 annotated chunks) is documented in the journal. The skill's references mention the eval-floor result (`cov≥90`) but don't reproduce the debugging narrative.

**Why this branch matters**: without it, every §Teach landing risks polluting the skill with arc history. The skill becomes unmaintainable as the journal sections pile up.

---

## The Five-Step Landing Procedure

Universal across all extensible skills:

### 1. Audit before patching

- Read the target reference file in full
- Check working-tree state (`git status`)
- Grep for existing coverage of the same topic
- Re-confirm the landing-target choice via the decision tree above (or `scripts/teach-route.mjs`)

### 2. Author the patch (skill-specific)

Where does the new content go in this skill's references/? How is it formatted? What surrounding sections does it impact? Map each branch to its primary reference file (see Decision Tree above).

### 3. Wire the activation surface

- Trigger keywords in SKILL.md frontmatter `trigger:` block (if the new knowledge has new trigger phrases)
- Capability menu entry (only for new modes — usually not needed for §Teach landings)
- Binding-procedure line in §Posture or §FirstPrinciples (only for Branch F)

### 4. Version + CHANGELOG

- PATCH for citation strengthening / fact additions
- MINOR for new procedural sections / new modes
- MAJOR for renames / removed modes

### 5. Verify with audit-a2ui-roster

```bash
node scripts/audit-a2ui-roster.mjs --strict
# expect: all axes green
```

Plus the eval gate if the landing was strategy/calibration-related:

```bash
npm run eval:diff -- --engine zettel
npm run eval:diff -- --engine free-form
```

---

## The 7 Anti-Patterns

Universal across all extensible skills. Each one breaks the skill in a specific way:

| # | Anti-pattern | What breaks |
| --- | --- | --- |
| 1 | **Append-only landing** | Content piles at end of section; semantic structure decays |
| 2 | **Substrate duplication** | Strategy code or chunk schema copied into skill prose; drift on next strategy change |
| 3 | **Orphan triggers** | Keywords added to frontmatter but no binding section in body |
| 4 | **Capability menu lies** | Menu item points to non-existent section or stub |
| 5 | **MINOR + PATCH bundling** | New procedural content cut alongside polish; muddied changelog |
| 6 | **Hygiene-debt deferral** | Audit regression noticed during landing, deferred to "next cut" |
| 7 | **One-way thinking** | Lands here without asking "should this be in a sibling skill?" (e.g., a chunk authoring rule might belong in `adia-ui-authoring`'s shell-patterns reference instead of here) |

---

## Quick-Reference Card

| Branch | Trigger | Lands at | SKILL.md change? |
| --- | --- | --- | --- |
| A | new chunk metadata field | chunk-authoring.md | no |
| B | new MCP tool | mcp/server.js + mcp-tool-reference.md | minor (mode 1 triggers) |
| C | new strategy / engine | strategies/ + strategy-engines.md | minor (mode 5 triggers + eval gate row) |
| D | new anti-pattern rule | anti-patterns.md + validator/checks/ | minor (mode 8 triggers) |
| E | calibration tune | composer.js + zettel-calibration.md | no |
| F | methodology / posture | inline SKILL.md (§Posture / §FirstPrinciples) | MINOR bump |
| G | new fragment-graph node type | composer.js + fragment-graph.md | no |
| H | arc-specific story | docs/journal/ | **NEVER** |

When in doubt, **prefer Branch H** (journal) over a skill landing. Arc stories that age out are easy to ignore; orphan rules that linger in the skill are hard to remove.

---

## Cross-references

- `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md` — the Plan-Execute-Verify rationale this §Teach inherits (every landing closes the PEV loop).
- `scripts/teach-route.mjs` — the authoritative mechanized branch router.
- `adia-ui-authoring` / `adia-ui-release` — sibling skills; route content there when Branch 7 (one-way thinking) applies.
- `eval-diagnostics.md` — run after any Branch C / E landing.
- `strategy-engines.md` + `zettel-calibration.md` — the engine-side substrate.

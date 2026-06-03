# `migration-guide-authoring.md` — authoring the MIGRATION GUIDE when cutting a breaking release

> Loaded by **mode 11 (Author a migration guide)** and by **mode 1 / 2** whenever the cut is a **MINOR** (an API-surface break — removed/renamed prop, attribute, slot, event, token, or tag). The **producer** side of migrations: you are shipping the breaking change, so you author the guide section consumers will follow. Companion: `changelog-discipline.md` (the CHANGELOG records _what_ landed; the migration guide tells consumers _how to absorb it_).

This is the **producer counterpart** to consumer-side migration. When the framework ships a breaking release, `MIGRATION GUIDE.md` is the canonical record of every BREAKING item + its mechanical search-and-replace recipe. The **consumer side** (sweeping a consumer app's call sites with `git grep` + `perl -i -pe`, then verifying with the build gate) lives in the separate consumer/app-author plugin — it READS this guide. Your job here is to WRITE the section it reads.

> **Scope split (don't blur it):**
>
> - **Producer (this skill, this file)** — author the `MIGRATION GUIDE.md` version section + migrate the IN-REPO surfaces (demo / exemplar / playground / catalog pages) so the release ships clean.
> - **Consumer (separate plugin)** — sweep a downstream consumer app against a published guide section. NOT this skill.
> - **Designing the breaking change itself** — a contract decision, not a migration. Upstream of both.

---

## §When you need a migration guide section

Author (or extend) a `MIGRATION GUIDE.md` section when the cut removes or renames a **public API symbol**:

- a removed/renamed **prop or attribute** (e.g. `variant="danger"` → `color="danger"`);
- a removed/renamed **slot** or **slot semantics flip** (e.g. `[open]` default-hidden → `[collapsed]` default-visible);
- a removed/renamed **event name** (e.g. `chat-submit` → `submit`);
- a removed/renamed **token** (e.g. `--n-*` → `--a-*`);
- a removed/renamed **tag** (e.g. `app-shell` → `adia-shell`);
- a **Boolean → enum** migration (e.g. `completed` → `status="completed"`);
- a **default-value behavior change** wide enough that consumers must act.

This is the same line as the **PATCH-vs-MINOR** rule in `cycle-happy-path.md` §Step 4b: **MINOR is reserved for API-surface breaks ONLY.** If you're cutting MINOR, you almost certainly owe a migration-guide section. If the change is a visible-behavior change with no removed/renamed symbol, it stays PATCH and usually needs only a CHANGELOG `### Changed` bullet — **not** a guide section.

Additive cuts (new component, new opt-in attribute, new API) need **no** migration section — note "additive; no consumer sweep" in the version table and move on.

---

## §Where the guide lives

`MIGRATION GUIDE.md` is a **top-level consumer artifact at the repo root** (not under `docs/` — the space in the filename is intentional; it's surfaced to consumers as a first-class document). It is READ by the consumer side but MODIFIED only here, at producer time, when a new breaking release is cut.

One section per release that introduces breaking changes, newest at the top. A consumer jumping multiple versions reads the merged span of all sections between their source and target.

---

## §The authoring workflow

### Step 1 — Enumerate the breaking surface

From the cut's diff + CHANGELOG `[vX.Y.Z]` `### Removed` / `### Changed` entries, list every breaking item. For each, capture:

- **The symbol** — the exact prop / attr / slot / event / token / tag.
- **The before → after** — old shape and new shape.
- **The kind** — pure rename (mechanical) · semantic flip (needs author judgment) · Boolean→enum · removal (no replacement).
- **The audit grep** — the `git grep -nE` that surfaces call sites.
- **The sweep** — the `git grep -lE | xargs perl -i -pe` incantation, OR "manual review" if the change can't be safely mechanized.

### Step 2 — Write the section

Section skeleton (per release):

```markdown
## Migrating to @adia-ai/web-components@X.Y.Z (YYYY-MM-DD)

<one-line scope: how many breaking items, the headline.>

### <item 1 — bold headline> (`old` → `new`)

<one sentence: what changed and why.>

**Audit:**

\`\`\`bash
git grep -nE '<pattern that surfaces call sites>'
\`\`\`

**Sweep:**

\`\`\`bash
git grep -nlE '<pattern>' \
  | xargs perl -i -pe 's/<old>/<new>/g'
\`\`\`

### <item 2 …>
...
```

Shape rules:

- **One item = one subsection.** Each removed/renamed symbol gets its own `###` with audit + sweep (or a "manual review" note).
- **Bold-prefix headline + before→after in the heading** — readers grep the heading for the symbol they hit.
- **Audit grep first, sweep second.** The consumer side ALWAYS audits (lists call sites) before sweeping. Author both so they can.
- **Mechanical vs manual, explicitly labeled.** A pure rename ships a `perl -i -pe`. A semantic flip / opt-out-Boolean / ownership-move ships a **"manual review — here's why"** note instead, because sed can't tell author intent (see §Manual-review classes below).
- **One component per sweep regex.** Don't merge `<(toast|alert|tag)-ui …>` alternations — perl/sed alternation captures don't preserve the matched alternative cleanly. One component at a time.
- **HTML-attribute regexes only match HTML/JSX.** A `<button-ui variant="danger">` sweep won't touch JS `el.variant = 'danger'` — author a separate JS-side regex when the symbol has a programmatic form.

### Step 3 — Migrate the in-repo surfaces FIRST

Before the cut ships, sweep the framework's OWN consumer surfaces — the demo pages, exemplars, playgrounds, and catalog — so the release doesn't ship broken examples of the thing it just changed. Run your own audit + sweep against `apps/`, `playgrounds/`, `catalog/`, `packages/web-components/components/*/*.html`. This is the producer dogfooding the migration: if the in-repo sweep is awkward, the consumer sweep will be worse — fix the recipe now.

### Step 4 — Verify

Run the cut's normal pre-flight gate roster (`cycle-happy-path.md` §Step 3). For a breaking cut, pay special attention to the structural/demo gates (`check:demo-shells`, the static-HTML probes) — they catch in-repo surfaces you missed. A **sweep-verification grep audit** across all extensions catches the trap where a vocabulary migration touched the markup but NOT the CSS selectors that style it or the JS comments that reference it (different files; a markup-only commit looks complete but leaves drift):

```bash
# For any vocabulary migration where legacy → new shapes coexist or get
# retired, grep the full legacy-pattern set across ALL extensions at the
# END of the in-repo sweep. 0 hits = sweep verified clean.
LEGACY_PATTERNS=( '<old-tag' 'old-attr=' '--old-token' )
for pat in "${LEGACY_PATTERNS[@]}"; do
  echo "=== $pat ==="
  grep -rln -E "$pat" apps playgrounds catalog \
    --include='*.css' --include='*.html' --include='*.js' --include='*.yaml' 2>/dev/null
done
```

### Step 5 — Cross-reference from the CHANGELOG + release notes

- The breaking package's CHANGELOG `[vX.Y.Z]` `### Removed` / `### Changed` entry should name the symbol AND point at the guide ("see `MIGRATION GUIDE.md` §X.Y.Z").
- The release notes (`notes-authoring.md`) carry a `⚠️` heads-up paragraph naming the break + linking the guide section, so consumers reading the announcement know to migrate.

---

## §Manual-review classes (do NOT auto-sweep)

Some breaking changes look mechanical but aren't. Document them as **manual review** with the reason, never as a `perl -i -pe`:

- **Semantic flips** — a rename that inverts default behavior. Example: `[open]` (default-hidden, opt-in) → `[collapsed]` (default-visible, opt-out). The right migration depends on author intent: if the surface wanted the thing expanded, drop the attr; if hidden, add `collapsed`. List occurrences, ask.
- **Opt-out Booleans that default true** — when `<x-ui filterable>` is the same as bare `<x-ui>` (filter on by default), the migration only matters where a consumer EXPLICITLY disabled an affordance (`searchable="false"`). Sed can't tell the difference.
- **Ownership moves** — moving a message/prop from a wrapper to a child (e.g. `<field-ui error="…">` → the message moves to the slotted control) requires knowing which child is the form control; the slot may not exist yet. Manual.
- **kebab-string property keys** — when the HTML _attribute_ name is unchanged but the JS _programmatic_ form changed (`el['submit-label']` → `el.submitLabel`), attribute-only consumers need no migration. Audit programmatic access only.
- **Wide tag/token renames (50+ symbols)** — the `@agent-ui-kit/*` → `@adia-ai/*` namespace rename class: tag renames, token-namespace renames (`--n-*` → `--a-*`), class renames (`NanoElement` → `AdiaElement`). Don't auto-sweep the whole surface blind — false positives are likely (a `variant="danger"` on a non-`*-ui` element that shares a prefix). List by table; require human approval per cluster.

---

## §The version-coverage table

Maintain a table at the top of `MIGRATION GUIDE.md` that classifies every release so a consumer jumping a gap knows which sections apply:

```markdown
| Version | Type | Sweeps |
|---|---|---|
| `0.0.22` | additive | New shell components; net-new APIs. No consumer sweep needed. |
| `0.0.21` | additive (no runtime change) | JSDoc/source-doc refresh. Bump the dep; no sweep. |
| `0.0.20` | BREAKING (N items) | <bullet list of every breaking item + its sweep>. |
| `0.0.5`–`0.0.19` | additive | No migration sweeps. Bump the dep version. |
| `0.0.4` | structural | Runtime extracted to a new package; imports retarget. |
| `@agent-ui-kit/*` → `@adia-ai/*` | rename | Tag + token + class renames (50+). Don't auto-migrate without approval. |
```

`additive` = bump and go. `BREAKING` = the version has a `###` section with audit + sweep per item. `structural` = import retargeting (package extraction / move). `rename` = wide namespace rename, manual-review by cluster.

---

## §Forward-looking surfaces (the next guide author's heads-up)

When a surface is currently additive but accumulating breaking pressure, note it at the bottom of the guide so the NEXT breaking-release author knows where the churn is concentrated — shell components, the gen-UI MCP op-type names, table-family opt-out attributes, etc. A future author reading "this area is volatile" writes a tighter section faster.

---

## §Anti-patterns

- **Authoring the guide AFTER the cut ships.** The guide section is part of the breaking-release scope — write it in the same cycle, before the in-repo sweep, so you dogfood the recipe.
- **A `perl -i -pe` for a semantic flip.** If author intent decides the migration, it's manual review. A mechanical sweep applied to a flip silently mis-migrates surfaces.
- **Merging component sweeps into one alternation regex.** One component per regex (capture-group preservation).
- **Skipping the in-repo sweep.** Shipping a breaking release whose own demo pages still use the old shape teaches consumers the wrong thing and trips the demo gates.
- **A bare CHANGELOG bullet with no guide section for a real break.** The CHANGELOG says _what_; the guide says _how_. A removed symbol needs both.
- **Treating this as the consumer sweep.** This skill authors the guide + migrates in-repo surfaces. Sweeping a downstream consumer app is the separate consumer/app-author plugin's job.

---

## §Verify target (mode 11)

The migration-guide section is "done" when:

1. Every breaking item in the cut's CHANGELOG has a matching `###` subsection (audit + sweep, or a labeled manual-review note).
2. The in-repo surfaces (demo / playground / catalog) are swept and the sweep-verification grep audit reports **0 legacy hits**.
3. The breaking cut's structural/demo gates pass.
4. The release notes carry the `⚠️` heads-up linking the guide section.

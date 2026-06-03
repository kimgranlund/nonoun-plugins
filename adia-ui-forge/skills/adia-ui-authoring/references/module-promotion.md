# Promote inline → module — Mode 4

Use when you find the same UI block (markup + controller JS) authored in two or more consumers — typically the docs shell (`site/`) and a playground (`playgrounds/<name>/`) — and need to lift it into a single reusable element under `packages/web-modules/<cluster>/<name>/`.

This reference codifies the **5-phase arc** proven on `<theme-panel>`. Phases are independent commits — trivially revertible.

Absorbed from the legacy `promote-inline-to-module` skill (now a redirect; this file replaces the daily-driver content).

> See [shell-patterns.md](shell-patterns.md) for the **different** activity of decomposing a single shell into a family of bespoke child elements per ADR-0023. This reference is for the _cross-cluster_ case where a single control surface (theme panel, command palette, future notification center, future user-menu) needs to live as one element used by many shells.

---

## When to use

- A consumer-authored inline block appears (with non-trivial drift) in 2+ surfaces, AND
- The block has a stable, semi-public API surface (4–10 props at most), AND
- The bug-surface from drift is real (e.g. behavior B is wrong relative to behavior A — playground "always shows 1,1" vs docs "reads computed").

## When NOT to use

- The duplication is ≤ 10 lines and has zero behavior drift — leave it inline.
- The element is genuinely shell-internal (admin-only, chat-only) — use [shell-patterns.md](shell-patterns.md) instead.
- The block is a CSS-only template — promote to `catalog/ui-patterns/` not `packages/web-modules/`.
- The block is a primitive (composes < 3 other primitives, no state) — promote to `packages/web-components/components/` instead.

## The 5-phase arc

Each phase = one commit. Each independently revertible. Verification gate runs at the end of every phase before the commit.

### Phase 1 — Author the element

1. `mkdir -p packages/web-modules/<cluster>/<name>` (new cluster, or under an existing one — see "Cluster placement" below).
2. Author **7 files** mirroring `web-modules/shell/admin-sidebar/`:

   ```text
   <name>.yaml             # source of truth — schema + a2ui rules + keywords
   <name>.js               # UIElement subclass; light-DOM; imperative DOM stamping
   <name>.css              # two-block @scope pattern per component-token-contract.md
   <name>.html             # standalone demo (loads <name>.examples.html via fetch)
   <name>.examples.html    # the matrix consumed by the live demo
   <name>.test.js          # vitest happy-dom — minimum 15 specs
   <name>.a2ui.json        # GENERATED — never hand-edit
   ```

3. Wire the **4 package.json + barrel touchpoints**:
   - `packages/web-modules/<cluster>/index.js` — `export { Name } from './<name>/<name>.js';`
   - `packages/web-modules/index.js` — add `export * from './<cluster>/index.js';`
   - `packages/web-modules/package.json` `exports` — add `"./<cluster>": "./<cluster>/index.js"` + `"./<cluster>/*": "./<cluster>/*/*.js"`
   - `packages/web-modules/package.json` `files` — add `"<cluster>/"`
   - `packages/web-modules/package.json` `sideEffects` — add `"./<cluster>/**/*.js"`
4. Regenerate catalog: `node scripts/build/components.mjs` — produces `<name>.a2ui.json` + updates the aggregate corpus catalog.
5. **Gate** before commit:

   ```bash
   node scripts/build/components.mjs --verify     # "clean — N files up-to-date"
   npm run verify:traits                          # 100%
   npm run smoke:engines                          # green
   npm run smoke:register-engine                  # 11/11
   npm run test:a2ui                              # 22/0/1
   npx vitest run packages/web-modules/<cluster>/<name>/<name>.test.js
   ```

### Phase 2 — Migrate primary consumer (typically `site/`)

The "full-fat" consumer — the one with persistence, prefers-color-scheme listeners, etc. This is your reference behavior; replicate its full surface in the module.

1. Replace inline markup with single-tag composition:

   ```html
   <popover-ui placement="bottom-end">
     <button-ui icon="palette" variant="ghost" size="sm" slot="trigger"></button-ui>
     <my-module slot="content" persist parametric presets scheme-toggle></my-module>
   </popover-ui>
   ```

2. **If the consumer has a sibling button that the module now absorbs** (e.g. a standalone `#theme-toggle` next to the popover trigger, which now lives inside the panel as `[scheme-toggle]`): retire the sibling button per **OD-002 = A**. Don't leave both.
3. Delete the controller blocks from `<consumer>.js`. Confirm via:

   ```bash
   grep -nE 'id="theme-default"|id="param-density"|id="preset-compact"' \
     site/index.html site/site.js
   # Expect zero hits.
   ```

4. **LS-key migration shim** — if the module uses a different storage namespace than the legacy controller, ship a one-shot read-old / write-new / drop-old block at the top of the consumer's boot script. Tested recipe:

   ```js
   // ── One-shot LS migration (YYYY-MM-DD) ──
   // TODO(YYYY-MM+60d): remove once all users have visited.
   {
     const oldToNew = {
       'adia-theme':        'adia-theme-scheme',
       'adia-theme-name':   'adia-theme-theme',
       'adia---a-density':  'adia-theme-density',
       'adia---a-radius-k': 'adia-theme-radius',
     };
     for (const [oldKey, newKey] of Object.entries(oldToNew)) {
       try {
         const v = localStorage.getItem(oldKey);
         if (v != null && !localStorage.getItem(newKey)) {
           localStorage.setItem(newKey, v);
         }
         if (v != null) localStorage.removeItem(oldKey);
       } catch {}
     }
   }
   ```

   Idempotent across reloads (second-run finds nothing to migrate). Add a removal TODO with a date 60+ days out.

5. **Gate**: `node --check` the consumer JS, grep for stale `#`-ids, manual visual QA at `npm run dev` if the user agrees to a foreground dev session.

### Phase 3 — Migrate secondary consumer (typically a playground)

The "stripped" consumer. Same structural change minus persistence.

1. Same markup substitution — **omit `[persist]`** so the playground stays ephemeral and doesn't leak state into the primary consumer on the same origin.
2. Delete the controller blocks. Drop any `const html = document.documentElement;` that is now unused. Keep primitive imports needed by the module's stamped children (text-ui, divider-ui, slider-ui, field-ui, button-ui, etc.).
3. Update the playground's `spec/SPEC.md` ASCII diagram to show the new tag.
4. **Gate**: same as Phase 2.

### Phase 4 — Migrate the chunk corpus

The harvested training-corpus chunk (`packages/a2ui/corpus/chunks/<name>.json`) embeds the consumer's HTML as an escaped string. Update it so the LLM sees the new authoring shape.

1. **Preferred** — re-run the harvester:

   ```bash
   npm run harvest:chunks
   ```

   Confirm `SOURCES` in `scripts/build/harvest-chunks.mjs` includes the consumer's directory (post-ADR-0026 it should include `site/pages`, `apps`, `playgrounds`, `catalog`).

2. **Fallback** — if the harvester source list excludes your consumer, edit the chunk JSON directly via a Python regex script. The pattern that worked for theme-panel:

   ```python
   pat = re.compile(
       r'<button-ui id="theme-toggle"[^>]*></button-ui>\s*'
       r'<popover-ui id="theme-popover"[^>]*>.*?</popover-ui>',
       re.DOTALL,
   )
   ```

   Refresh `captured_at` to today's ISO timestamp.

3. **Defensive grep across all chunks** for the legacy markers:

   ```bash
   grep -l 'id="<old-id>"' packages/a2ui/corpus/chunks/*.json
   ```

4. **Gotcha — hand-edit + later re-harvest** — if you used the fallback (step 2) AND a peer later adds your consumer's directory to harvester SOURCES, the next `harvest:chunks` run will overwrite your hand-edit with the live consumer HTML. Usually that's _good_ (the re-harvest captures the live state, including any post-edit consumer updates), but diff before assuming. Concrete example: theme-panel's `playground-app-shell.json` was hand-edited, then re-harvested after `playgrounds/` was added to SOURCES — the re-harvest captured the `<aside-ui>` → `<admin-sidebar>` bespoke conversion that the hand-edit missed.
5. **Gate**:

   ```bash
   npm run test:a2ui                              # 22 pass — chunk loads
   npm run smoke:chunks                           # tolerate pre-existing failures
   # Optional (real-LLM, ~$2 per full eval):
   npm run eval:diff -- --engine zettel           # cov ≥ 40, avg ≥ 85
   ```

### Phase 5 — Release

Either ship as a standalone lockstep cut (per the **adia-ui-release** skill, lockstep release mode), OR ride a bundled cut that the user is already coordinating. Either way:

1. **CHANGELOGs** — `packages/web-modules/CHANGELOG.md` `[Unreleased]` (or the dated bump block if you're cutting now) + root `CHANGELOG.md`.
2. **README** — `packages/web-modules/README.md`: cluster table row, Layout tree entry, Quick start `import` line.
3. **Spec status** — `docs/specs/<name>-module.md` Status field flips `Draft — proposed` → `Active — shipped vN.M.P`, plus the phase-table tick.
4. **Specs INDEX** — `docs/specs/INDEX.md` row status column.
5. **Journal** — per the repo's journal discipline, every non-trivial phase lands a `## §N — <topic>` in the dated journal the same turn it commits — don't batch-write at release. Phase 5 adds a _closing_ `§N` covering the release itself (lockstep cut, deploy, what changed at the package boundary). The release section's commit SHAs + verification table close the arc; future archeology starts here.
6. **Plan** — front-matter Status → `Completed — shipped`.

## Cluster placement decision (OD-001)

| Option | When to pick |
| --- | --- |
| **A. New cluster** | The element is its own product axis; ≥ 2 credible siblings are foreseeable (e.g. `theme/` cluster: theme-panel today, theme-toggle + theme-preview tomorrow). Cost: 4 single-line edits (cluster `index.js`, root barrel, 3 `package.json` entries). |
| **B. Existing cluster** | The element fits a current family with no expansion plans. Pick the **most cross-cutting** cluster (`simple/`, `runtime/`) before a shell-specific one (`shell/`, `chat/`, `editor/`). |
| **C. Inside a shell cluster** | Almost never — fails if the element is consumed by _other_ shells. Use only when the element is structurally shell-bound. |
| **D. Promote to primitive** | Only if it composes < 3 other primitives. Most controls fail this test. |

## Two rules from observed bugs

### OD-002 — Absorb the standalone-button-next-door

When the original duplicated markup has a sibling button that conceptually belongs with the panel (e.g. `<button-ui #theme-toggle>` flipping `color-scheme` next to the `<popover-ui>` that contains the theme panel), **absorb it into the module behind a boolean attribute**, don't leave it next door. Two duplications collapse into zero.

Module shape:

```html
<my-module scheme-toggle></my-module>
<!-- renders an internal <segmented-ui> at the top of the panel -->
```

The sibling button retires from consumer markup. Programmatic alternative stays available via `.apply({scheme})`.

### OD-003 — Read computed values back into controls

When the module owns sliders that mirror CSS custom-property values that a _theme_ (or other parent) sets, the user mental model is "the slider shows the current value, regardless of how it got there." So on theme-change:

```js
target.style.removeProperty('--a-density');  // clear local override
target.style.removeProperty('--a-radius-k');
// theme [data-theme] block now takes effect

requestAnimationFrame(() => {
  const cs = getComputedStyle(target);
  this.#densityEl.value = parseFloat(cs.getPropertyValue('--a-density')) || 1;
  this.#radiusEl.value  = parseFloat(cs.getPropertyValue('--a-radius-k')) || 1;
});
```

The `requestAnimationFrame` matters — CSS application is async with attribute write; reading on the next frame guarantees the computed value reflects the new theme block.

The bug this fixes: a stripped-down playground variant that resets sliders to `1, 1` on theme click. Sliders then lie about the current value (`1.5` is the actual radius for `[data-theme="ocean"]`).

## Peer-agent boundary discipline (cluster-promotion-specific notes)

**General peer-agent + stale-context rules are canonical in the repo's AGENTS.md "Multi-agent baseline assumption" guidance.** Read those first: turn-start `git status` / `log` / `fetch` checklist, never-`git add -A`, explicit-allowlist staging, re-baseline after peer commits, doc-currency coordination, "Excluded — peer-agent in-flight" commit-message rule.

**Journal cadence** is canonical in the repo's AGENTS.md "Journal docs (maintain as you go)" guidance — append `## §N — <topic>` to today's journal + INDEX bullet the same turn each phase commits, not batched at release. The "journal-sN-handoff" note pattern is for genuinely-blocked writers only (the file is locked by a peer mid-arc); default to direct edits.

What follows are the **module-promotion-specific** extensions, not covered by the generic AGENTS.md guidance:

1. **Catalog regeneration risk** — `node scripts/build/components.mjs` reads ALL yamls in `packages/web-components/components/` AND `packages/web-modules/`, so a regenerated aggregate corpus catalog will absorb any of the peer's uncommitted yaml changes (e.g. an in-flight `input-ui` rewrite). **Don't stage the aggregate catalog** if it would bundle peer work; let the next person to run the build regenerate it cleanly. Your per-component `<name>.a2ui.json` sidecar inside `packages/web-modules/<cluster>/<name>/` is sufficient on its own — that's what the per-component verify gate actually compares against.

2. **Chunk re-harvest may improve on your hand-edit** — if a peer adds your consumer's directory to `scripts/build/harvest-chunks.mjs` SOURCES while your migration is in flight, the next harvester run will pick up the live consumer HTML. That's usually **strictly better** than your hand-edit because it captures any in-flight bespoke shape updates the consumer received (e.g. `<aside-ui>` → `<admin-sidebar>` per ADR-0024). When you see a peer harvester run land, diff your Phase 4 hand-edit against the re-harvested chunk — if the re-harvest captures the new tag and is structurally cleaner, your hand-edit is superseded and nothing more to do.

3. **Module-promotion paths the peer may be editing** — the highest-overlap surfaces during a module-promotion arc are:
   - `packages/web-modules/index.js` (the root barrel — multiple clusters may want to add their `export *` lines in the same session)
   - `packages/web-modules/package.json` (exports/files/sideEffects — same)
   - The CHANGELOG block for the in-flight release

   Stage these explicitly file-by-file; check each diff before committing.

## Path-rebase awareness

Plans authored before architectural reorgs reference stale paths. Before executing, **grep for plan path references against the live tree**:

```bash
# Example: plan says apps/app-shell/; tree has playgrounds/admin-shell/
for p in $(grep -oE 'apps/[a-z-]+/' docs/plans/<plan>.md | sort -u); do
  test -d "$p" || echo "STALE: $p"
done
```

For ADR-0026 specifically: `apps/app-shell/` → `playgrounds/admin-shell/`; `apps/generic-shells/` → `apps/page-shells/`; `apps/patterns/` → `catalog/ui-patterns/`.

Note the rebased paths in your commit messages so future archeology is easy:

```text
Path note: plan references 'apps/app-shell/' (pre-ADR-0026 paths);
actual path is 'playgrounds/admin-shell/' under the 3-tier
apps/playgrounds/catalog layout.
```

## Pitfalls

1. **Skipping the `<name>.test.js` file.** Mandatory — peer references ([shell-patterns.md](shell-patterns.md)) demand a behavior test. Minimum coverage: stamp + connect, attribute reflection, primary user action, programmatic API, persistence on/off, disconnect cleanup. Target ≥ 15 specs; theme-panel ships 23.
2. **Forgetting one of the 4 `package.json` touchpoints.** Add to `exports` only, leave `files` out → `npm publish` ships a broken package (the directory isn't in the tarball). Add to `files` only, leave `sideEffects` out → bundlers tree-shake the `customElements.define()` call and the element silently never registers in production builds. All four are required.
3. **`[persist]` on by default.** Embedded demos silently mutate the docs shell's stored preferences (same origin). Default to ephemeral; flip `[persist]` on per-consumer.
4. **Editing the aggregate catalog by hand.** It's generated. Edit the `<name>.yaml` SoT and run `npm run build:components`.
5. **Bundling the LS-key shim with no removal date.** Future you won't remember to remove it. Always add `TODO(YYYY-MM+60d): remove …` near the shim.
6. **Promoting to a primitive instead of a module.** If the element composes existing primitives (button, slider, field, popover, etc.), it's a module per ADR-0012. Primitives are atomic by contract.

## Verification checklist

- [ ] All 5 phases land as separate commits (revertible)
- [ ] `node scripts/build/components.mjs --verify` clean (N+1 files vs baseline)
- [ ] `<name>.test.js` ≥ 15 specs passing
- [ ] `npm run test:a2ui` 22 pass / 0 fail / 1 skipped
- [ ] `npm run check:lockstep` green (if you cut a release)
- [ ] All 4 `package.json` touchpoints + cluster barrel + root barrel updated
- [ ] Spec status flipped Draft → Active in same arc
- [ ] CHANGELOGs (package + root) + README + journal updated
- [ ] No stale `#<old-id>` references in consumers (`grep -nE 'id="<old-prefix>-'`)
- [ ] LS-key shim has a removal TODO date (if applicable)
- [ ] Peer agent's files NOT staged in your commits

## Cross-references

- [shell-patterns.md](shell-patterns.md) — mode 3 (bespoke shell tier decomposition, ADR-0023; the _different_ activity)
- [authoring-cycle.md](authoring-cycle.md) — the standard 5-step authoring cycle (mode 1 / mode 2)
- [api-contract.md](api-contract.md) — prop naming, reflection, the legacy forms
- **adia-ui-release** (sibling skill) — lockstep release cycle (Phase 5)
- **adia-ui-a2ui** (sibling skill) — chunk corpus harvest + smoke gates (Phase 4)
- Spec: `docs/specs/package-architecture.md` — three-tier package layout
- ADR-0012 — primitives vs modules vs themes
- ADR-0023 — bespoke shell pattern (mode 3 reference)

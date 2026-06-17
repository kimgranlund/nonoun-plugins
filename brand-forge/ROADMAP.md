# Roadmap

## Planned

<!-- Features and improvements for a future version. -->
<!-- Format: - [vX.Y] Description -->

- [v0.5] **Council-calibration eval** — _**LANDED** 2026-06-04 (`evals/council-calibration/`):_ a planted-defect strategy fixture (`weak-brand-strategy.md` — every `rubric-brand-strategy` anti-pattern + the bullshit filter), a transcript checker, a protocol, and a recorded baseline. Run cold, the brand council caught **6/6** planted defects and returned REBUILD; the trust boundary held (the fixture's self-description was treated as data, not an instruction). _Deepened (2026-06-10 → 06-12):_ catch-rate over **N=3** reached on **all three sub-councils** (strategy/Northwind 6/6 · design/Lumina 5/5 · voice/Verve 5/5, each ×3) **and the `brand-muse` seat** (Halcyon 6/6 ×3) — the Muse extension landed by **inverting the harness**: `check-muse.py` scores the moves the Muse must MAKE (name the category center, ground the pull in a real root over a moodboard, commit a differentiating bet, raise to an ideal, direction-not-slogan, ST5 seat-separation) rather than defects it catches, closing the un-calibrated-quality gap the panel could package but not judge. _Still open:_ a multi-lens Muse fan-out (below) if aspiration diversity earns it.
- [v0.5] ~~**Stamp-output validation in CI.**~~ **LANDED 2026-06-17 (0.4.21).** `evals/stamp-smoke/corpus/` (a tiny two-layer corpus) is stamped by `bin/brand-stamp plugin` in CI, then run through `plugins-factory/bin/validate_plugin.py --strict` (passes 0/0) — closing the generator-untested gap the v0.2 red-team flagged (David F., S9/S10). Lives in CI: the only legal place to orchestrate brand-stamp → validate_plugin without a cross-plugin dependency.
- [v0.5] ~~**A real "Brand Stack" deliverable, if it earns its place.**~~ **LANDED 2026-06-17 (0.4.22).** Built properly: six tiers (Root · Position · POV · Expression · Product · Stewardship) **defined in `brand-methodology`** (`references/brand-stack.md`) as a tier↦corpus-layer map (so it can't drift from the canon), a thin `/brand-stack` command, and `templates/brand-stack-one-pager.md`. A condensed at-a-glance reading distinct from `/brand-stamp`'s full export; maturity shown, never faked; **no dangling bin** (content-condensation is the model's job, not a script's).

- [v0.5] **A multi-lens Muse fan-out.** v0.4 ships a single Muse agent carrying its lenses internally; if aspiration diversity proves as valuable as critic diversity, promote the lenses to parallel isolated muse agents (the ideal · the contrarian · the analogical · the principles) fanned out like the council — the generative mirror of the critic panel.
- [v0.5] **Making roles as optional maker agents.** The Team's seats are methodology knowledge today (adopted on demand within `/brand-build`). Promote a seat to its own isolated agent only where an isolated context earns its cost (e.g. a dedicated Copywriter for long voice work) — never for mere symmetry with the council.

- [v0.5] ~~**A concept-consistency gate.**~~ **LANDED 2026-06-17 (0.4.21).** `bin/check-concepts.py` (selftested, CI-wired) flags a retired seat-term — `provocateur` (the old seat name) or "widen the options" (the old seat job) — in a seat-defining surface (`agents/` · `skills/` · `commands/`), the structural check the plugin's thesis demands. **Precise:** it does NOT flag the still-valid "provocation"/"provokes" (a provocation is one shape the gravitational pull can take), so it caught the rename class without false-positiving on living vocabulary; skips `CHANGELOG`/`reviews`/`.name-map.md`.

## Deferred

<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->

- **`get_brand_tokens` returning `isError:true` on not-found** — the v0.2 red-team flagged it returns `isError:false`, unlike `fetch_brand_section`. Kept deliberately: "no tokens in the corpus" is an empty-survey result (like `search`/`list` returning nothing), not a failed path lookup. Revisit only if a consumer model demonstrably mishandles the empty case. See `reviews/2026-06-03-v0.2-red-team.md` SHOULD-fix #6.
- **Trimming the council roster** — 14 critics is the product; none has been demoted. Re-evaluate roster size only if the calibration evals above show overlapping lenses.

## Out of scope (by design)

<!-- Capabilities explicitly excluded — not postponed, intentionally outside this plugin's boundary. -->

- **Product / UX strategy** — that is `product-forge`'s domain. brand-forge owns brand strategy, identity, voice, and stewardship, and defers product-experience concerns across that boundary.
- **Plugin-lifecycle tooling** — carving, manifest-wiring, and adversarial plugin review are `plugins-factory`'s job. brand-forge is authored _by_ it, not a peer of it.
- **Shipping a specific brand's corpus** — the `.mcp.json` declares a retrieval _slot_; the plugin never bundles a brand's data. Per-instance corpus is wired via `userConfig.corpus_dir`.

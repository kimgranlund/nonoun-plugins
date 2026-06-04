# Roadmap

## Planned

<!-- Features and improvements for a future version. -->
<!-- Format: - [vX.Y] Description -->

- [v0.5] **Council-calibration eval** — _**LANDED** 2026-06-04 (`evals/council-calibration/`):_ a planted-defect strategy fixture (`weak-brand-strategy.md` — every `rubric-brand-strategy` anti-pattern + the bullshit filter), a transcript checker, a protocol, and a recorded baseline. Run cold, the brand council caught **6/6** planted defects and returned REBUILD; the trust boundary held (the fixture's self-description was treated as data, not an instruction). _Open (deeper):_ a catch-rate over N runs (not one), more fixtures (a borrowed-provenance-only deck; a logo-that-dies-at-16px for the `design` sub-council; a hollow voice spec for `voice`), and **extend it to the `brand-muse`** — assert the aspiration traces to a cultural root and pulls the work off the category average (the Muse has the same un-calibrated-quality gap the panel can package but not yet judge).
- [v0.5] **Stamp-output validation in CI.** `bin/brand-stamp` emits child plugins "authored to pass `validate_plugin.py`," but nothing asserts the generated output actually does. Add a CI fixture that stamps a tiny corpus and runs the harness validator on the result, closing the generator-untested gap the v0.2 red-team flagged (Farley, S9/S10).
- [v0.5] **A real "Brand Stack" deliverable, if it earns its place.** The orphaned six-tier renderer was removed in v0.2 because the methodology never adopted the model. If a one-pager export is wanted, build it properly — the six tiers defined in `brand-methodology`, a wired command, and a template — not a dangling bin.

- [v0.5] **A multi-lens Muse fan-out.** v0.4 ships a single Muse agent carrying its lenses internally; if aspiration diversity proves as valuable as critic diversity, promote the lenses to parallel isolated muse agents (the ideal · the contrarian · the analogical · the principles) fanned out like the council — the generative mirror of the critic panel.
- [v0.5] **Making roles as optional maker agents.** The Team's seats are methodology knowledge today (adopted on demand within `/brand-build`). Promote a seat to its own isolated agent only where an isolated context earns its cost (e.g. a dedicated Copywriter for long voice work) — never for mere symmetry with the council.

- [v0.5] **A concept-consistency gate.** The v0.4 reframe (provocateur → attractor) leaked the retired seat-verb into three docs because nothing gates a concept-rename the way `reference-lint` gates broken links. Add a CI sweep that flags a deprecated seat-term ("provoke" / "widen the options") in seat-defining context (outside `CHANGELOG`/`reviews`) — the structural check the plugin's own thesis ("structure is mechanized; taste is not") demands.

## Deferred

<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->

- **`get_brand_tokens` returning `isError:true` on not-found** — the v0.2 red-team flagged it returns `isError:false`, unlike `fetch_brand_section`. Kept deliberately: "no tokens in the corpus" is an empty-survey result (like `search`/`list` returning nothing), not a failed path lookup. Revisit only if a consumer model demonstrably mishandles the empty case. See `reviews/2026-06-03-v0.2-red-team.md` SHOULD-fix #6.
- **Trimming the council roster** — 14 critics is the product; none has been demoted. Re-evaluate roster size only if the calibration evals above show overlapping lenses.

## Out of scope (by design)

<!-- Capabilities explicitly excluded — not postponed, intentionally outside this plugin's boundary. -->

- **Product / UX strategy** — that is `product-forge`'s domain. brand-forge owns brand strategy, identity, voice, and stewardship, and defers product-experience concerns across that boundary.
- **Plugin-lifecycle tooling** — carving, manifest-wiring, and adversarial plugin review are `plugins-factory`'s job. brand-forge is authored _by_ it, not a peer of it.
- **Shipping a specific brand's corpus** — the `.mcp.json` declares a retrieval _slot_; the plugin never bundles a brand's data. Per-instance corpus is wired via `userConfig.corpus_dir`.

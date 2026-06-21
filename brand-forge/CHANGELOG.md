# Changelog

## [0.4.34] — 2026-06-20

### Added

- **Exemplar enrichment (increment 5) — option-generation seeds, by domain and axis.** `skills/brand-guidelines/references/exemplars.md`: per-domain exemplars keyed to where they sit on the 2×2 axes, so a generated card reads *"like X — which does Y"* rather than a generic option. **Mechanism-level + citation-only by design** — cite what a brand does and why it works, never reproduce its assets; link-only for anything deeper; an exemplar proves a move is *possible*, it's not a license to copy (the move must still trace to `01-foundation`). Explicitly **non-duplicative of brand-decomposer** (points at its curated catalog for the deep reference set; this is the maker-side seed list, not a grading bar). Linked from the `brand-guidelines` SKILL + `the-loop.md`.
- **This completes the brand-guidelines system** (the 5-increment plan in `docs/designs/brand-guidelines-system.md`): the 2×2 elicitation loop (`/brand-elicit`) → the validated choice-ledger → coverage + the deterministic assembler (→ corpus docs, `corpus-provenance`-gated, `brand-evaluate`-scored) → the brand-decomposer card-projection seam → cross-domain coherence → exemplar seeds. plugin.json 0.4.33 → 0.4.34.

## [0.4.33] — 2026-06-20

### Added

- **Cross-domain coherence (increment 4) — the loop now reads the graph.** `bin/guidelines-ledger` gains **`coherence <ledger> [--domain <d>] [--strict]`**: the mechanized half of cross-domain coherence — given a domain being framed, it computes the **prior commitments** the new domain's 2×2 should cohere with (the live choices in already-decided domains), the **graph edges** touching it, and any **`contradicts`** edges to resolve. `/brand-elicit` calls it before framing each domain so options honor earlier choices and a contradiction is surfaced (the computation is code; the resolution stays judgment — coherence informs, it doesn't railroad). `--strict` exits non-zero on any unresolved contradiction (gateable).
- **Stronger ledger validation:** a graph edge's `from`/`to` must now be a real domain or an existing entry id (a dangling coherence ref is caught at `validate`, not discovered later). The `move` `severity` enum (added 0.4.31) and the graph edges round out the typed schema.
- Selftest extended (coherence surfaces commitments/edges/contradictions; a dangling graph ref is rejected); docs (`brand-guidelines` SKILL + `the-loop.md` + `/brand-elicit`) updated to call `coherence` in the framing step. No new command/skill (bin mode). plugin.json 0.4.32 → 0.4.33.

## [0.4.32] — 2026-06-20

### Added

- **The brand-decomposer card-projection seam (increment 3) — the make→grade handoff.** `bin/guidelines-ledger card <ledger> [--idea "..."] [-o card.json]` projects the live choice-ledger into a `*.brand.json` card matching `design-skills:brand-decomposer`'s documented shape: each chosen design-move becomes a typed `rule` (`truth: proposed` — the designer chose it; `evidence` points back at the ledger entry, so it's traced), the brand idea from `--idea` (the foundation), with `domains` rolled to the six. brand-forge MAKES; brand-decomposer GRADES — **parallel, not a dependency** (different marketplace, self-contained): the projection is best-effort to brand-decomposer's documented shape, not a hard contract.
- **Verified end-to-end (locally — CI can't reach a sibling marketplace):** a projected card **clears brand-decomposer's operability gate** via its real `brand-spec-check.py lint` (well-formed · traced · accessible · complete), with one honest `surfaces[]` incompleteness warn (the elicitation captures directional rules, not surface enumeration — accurate, not a defect). The bin's selftest covers the projection shape (brand/idea, the six domains, each rule's domain/severity/evidence/`proposed`-truth, projection from the ledger entry).
- Docs (`brand-guidelines` SKILL + `the-loop.md` + `/brand-elicit`) updated — the seam is built. This completes the core make→assemble→provenance→evaluate→grade arc; the remaining increments (the cross-domain coherence graph, exemplar enrichment) are refinements. plugin.json 0.4.31 → 0.4.32.

## [0.4.31] — 2026-06-20

### Added

- **The guidelines assembler + coverage (increment 2) — the build loop closes into the corpus.** `bin/guidelines-ledger` gains two modes: **`coverage <ledger>`** (per-domain resolved/absent + the frontier still to elicit) and **`assemble <ledger> --out <corpus> [--flat] [--apply]`** — a **deterministic** compile (no inference) of the *live* ledger (supersessions applied) into per-domain corpus docs: each domain's choices → its mapped layer (`mark`→`03-identity`, `color`/`type`/`expression`→`04-expression`, `voice`→`05-voice`, `governance`→`07-guidelines`), every choice rendered as a **typed rule** (`must/should/may`, default `should`) with rationale · effect · exemplar · ledger-trace, each doc stamped with **`sources:`** (the ledger it traces to) + **`contributors:`** (designer + system) frontmatter. It **matches the corpus's flat/folder convention and refuses a mixed corpus** (the never-mix rule), and is **dry-run until `--apply`**. The move schema gains an optional `severity` (`must/should/may`, validated).
- **The loop closes — proven end-to-end.** An assembled corpus **passes `corpus-provenance` clean** (the `sources:` resolve to the ledger; `contributors:` present) and is then scorable by `/brand-score` (`brand-evaluate`): build → assemble → provenance-gated → scored. A new CI step runs the full chain (template → validate → assemble → corpus-provenance) so the closure is gated, not just claimed; the bin's selftest covers coverage, supersession-honoring, assemble dry-run/apply, and mixed-corpus refusal.
- Docs (`brand-guidelines` SKILL + `the-loop.md` + `/brand-elicit`) updated — assembly/coverage are now live; the brand-decomposer card-projection seam is the next increment. plugin.json 0.4.30 → 0.4.31.

## [0.4.30] — 2026-06-20

### Added

- **`/brand-elicit` — build a guidelines section by guided 2×2 choice (the elicitation maker, increment 1).** A new command (routing to the new `brand-guidelines` skill) that walks the six brand domains (`mark · voice · color · type · expression · governance`); for each it crosses two of the seven exploration axes into a **2×2**, generates four concrete **design-move cards** grounded in `01-foundation` + a cited exemplar, the designer picks **A/B/C/D + comments/corrections**, and the choice is appended to a typed **choice-ledger** that accumulates into a coherent, evidence-traced guidelines corpus. Defaults: one-quadrant-plus-comments pick model (a "blend" is captured as an amended single choice); a deterministic default axis-pair per domain (the model may swap with a stated reason; the designer may override).
- **`bin/guidelines-ledger`** — validates the choice-ledger **well-formed by construction** (the score-record/assess-record discipline): domain ∈ the six, chosen ∈ the presented quadrants, exactly two distinct axes from the seven, the design-move's required fields + confidence band, non-empty contributors, `supersedes` referencing only an earlier entry, no duplicate ids, and graph edges using brand-decomposer's relationship vocabulary. Modes: `validate · template · schema · selftest` (the gate proves itself across every malformation); CI-wired alongside the other corpus tools.
- **Squared with `design-skills:brand-decomposer` (parallel, NOT a dependency).** brand-decomposer GRADES/decomposes/critiques a brand spec; `brand-guidelines` MAKES one. The skill mirrors brand-decomposer's six domains + seven axes + evidence discipline as **vocabulary** (restated, not imported — it's a different marketplace and brand-forge is self-contained) and will hand it gradeable output via an optional card-projection seam (a later increment). The rubric/schema/operability-checker are NOT duplicated.
- **Scope:** this is the net-new maker loop + the validated ledger. The deterministic **assembler** (ledger → corpus docs with `sources:`/`contributors:`, gated by `corpus-provenance`, scored by `brand-evaluate`), the coverage check, and the brand-decomposer card-projection seam are the next increments. Design: `docs/designs/brand-guidelines-system.md`. plugin.json 0.4.29 → 0.4.30 (9 commands, 4 skills).

## [0.4.29] — 2026-06-20

### Added

- **Stamp-output validation across all three forms — `brand-stamp verify` + `selftest` (closes the S9/S10 backlog item).** CI validated only the **plugin** stamp form; the **cloud-skill** and **standalone-MCP** forms could regress silently. `brand-stamp` gains a `verify <root> --form {plugin|skill|mcp}` mode that asserts each form's required structure — plugin: a valid `plugin.json`/`.mcp.json` + the bundled server + a `skills/<name>/SKILL.md`; skill: `SKILL.md` frontmatter (`name`/`description`) + a non-empty `references/` corpus **and no MCP/scripts** (the cloud form must stay pure); mcp: the server + a `README.md` with the `claude mcp add` recipe — plus, for the forms that ship the server, a **drift check** that the bundled `brand-corpus-mcp.py` is byte-identical to the canonical one. A `brand-stamp selftest` proves the gate (all three forms stamp + verify clean; an MCP leak in the cloud form, a broken `plugin.json`, and a drifted bundled server are each caught). **CI now stamps all three forms, `verify`s each, deep-validates the plugin form with `validate_plugin --strict`, and runs the stamped MCP's own selftest** — the catalog's named-gate-over-inline-assertion discipline (the check-bake-safety precedent). plugin.json 0.4.28 → 0.4.29.

## [0.4.28] — 2026-06-20

### Added

- **`bin/corpus-provenance` — the provenance/sources audit, mechanized.** The two provenance audit-checklist items the 0.4.27 work added were advisory prose; this makes them a **check**. `corpus-provenance <corpus>` parses each document's frontmatter and **fails (exit 1) on a broken `sources:` trace** — a reference that resolves to no file in the corpus, the exact defect retention exists to prevent — and **warns (exit 0)** on a 01–02 artifact missing `contributors` or a `sources:` ref resolving outside `00-sources`. Gated where it's a real defect, advisory where it's a judgment call. Detects both corpus conventions and resolves a `sources:` ref across them (a flat-style ref still resolves in a folder corpus, and back); a traversal ref is treated as a broken trace, never followed outside the corpus. Selftested (clean / dangling / missing-attribution / out-of-layer / cross-convention / traversal cases) and CI-wired alongside `corpus-migrate`. Referenced from `corpus-architecture.md` (audit checklist) + `brand-corpus/SKILL.md`. plugin.json 0.4.27 → 0.4.28.

## [0.4.27] — 2026-06-19

### Added

- **Source ingestion + retention — the `00-sources` layer.** The corpus now keeps the raw material a brand is *built from*, not only the brand it produces. `00-sources` slots in at load-order zero (above `01-foundation`): legacy brand books, research/interview transcripts, the founder's writing, competitor/cultural references — landed verbatim, **retained for the life of the corpus** (never deleted after they're synthesized into 01+), **archived not scored** for maturity, and treated as **untrusted DATA** (an instruction embedded in a source is a finding, not an order). It reuses the existing layer machinery: `bin/corpus-migrate` migrates it flat⟷folder like any layer (LAYERS + selftest extended), and the MCP enumerates it automatically.
- **Provenance & attribution — per-document frontmatter.** Every corpus document can carry `contributors` (who shaped it, by person or agent seat — `Muse`, `brand-copywriter`, `brand-council`, the client — each with role + date) and `sources` (the `00-sources` files it was synthesized from). This captures role-provenance git structurally can't (a corpus often lives in a Claude Project with no git; even under git the committer is one identity, never the *seat*), travels *with* the document, and links each artifact back to its retained evidence. **`brand-corpus-mcp` surfaces both** — `list_brand_documents` now reports each doc's contributors (`— by …`) and sources (`← …`) via a tolerant stdlib frontmatter parser (no yaml dependency); selftest extended (inline + block-form + no-frontmatter cases).
- **Docs:** `skills/brand-corpus/references/corpus-architecture.md` gains the `00-sources` layer, a **Source ingestion & retention** section (the 3-step ingest flow + the retention rationale + the trust boundary), a **Provenance & attribution** section (the frontmatter schema + why frontmatter over git/manifest), the manifest `00` row, and two audit-checklist items; `SKILL.md` gains the layer in the canonical structure + a **Sources, ingestion & attribution** pointer. plugin.json 0.4.26 → 0.4.27.

## [0.4.26] — 2026-06-17

### Added

- **`brand-evaluate` now ships a worked exemplar for every rubric family** (the skill's "extension point" made concrete — researched + authored to the rubric template). The three shipped rubrics were all strategy-adjacent (brief-quality, brand-strategy, creative-collaboration); two new exemplars give the **Visual** and **Voice** families their shape: **`rubric-visual-identity.md`** (identity coherence · type · color · expression-system fitness · editorial restraint · cross-surface consistency, scored against the **de-label test** — cover the logo, is it still this brand?) and **`rubric-brand-voice.md`** (tone consistency · nomenclature · copy principles · editorial voice, scored against the **refusal test** — what won't you say?). Both carry the trust-boundary anti-pattern. The library index now lists **four families with ≥1 shipped exemplar each (five total)**; the remaining ~17 dimensions stay the extension point a full corpus fills. plugin.json 0.4.25 → 0.4.26.

## [0.4.25] — 2026-06-17

### Added

- **The `brand-methodology` foundation-canon "Extension point" is now built — five component method references** (the skill's own deferred next-step; researched + authored in the methodology's own senior voice). The canon named five components a mature corpus expands into their own references; each now ships as a *method* reference (the method · what good looks like · the hard test · the anti-pattern), descending from the 3-page foundation: **`positioning-territories.md`** (stake ownable ground — the competitor-substitution test), **`category-design.md`** (design the container, not compete in it — "does anyone but you use the words?"), **`competitive-archaeology.md`** (read residual/dominant/emergent codes; honor/subvert/abandon; the double-recognition test), **`transformation-story.md`** (customer-as-hero, brand-as-guide; the before→after identity pair), and **`editorial-style-guide.md`** (voice vs tone; "what won't you say?"). `foundation-canon.md` + `brand-methodology/SKILL.md` point at all five. plugin.json 0.4.24 → 0.4.25.

## [0.4.24] — 2026-06-17

### Added

- **`brand-corpus`'s "Extension point" is now built, not just named** (the skill's own deferred next-step). `references/corpus-architecture.md` § Extension point used to *describe* four enrichments; all four ship: (1) a **per-layer maturity manifest** — the contents each of the eight layers expects before it's `mature`, with load-order binding 03–06 to a complete 01; (2) **`bin/corpus-migrate`** — the flat ⟷ folder convention migration as a tool (the architecture already called it mechanical): detects the shape, **refuses a mixed corpus** as a defect, renames every layer asset, dry-run by default with `--apply`, selftested (lossless round-trip, preserves non-layer files, tidies empty layer dirs); (3) **corpus templates per convention** (the manifest instantiated in either shape); (4) an **audit checklist → `08-evaluation`** (load-order, single-convention, per-layer manifest coverage, voice-shown, product-keeps-promise, live decision log). `brand-corpus/SKILL.md` points at the tool + the manifest. plugin.json 0.4.23 → 0.4.24.

## [0.4.23] — 2026-06-17

### Added

- **`brand-copywriter` — the first maker seat promoted to an isolated agent** (the v0.5 "making roles as maker agents" item). The Team's Copywriter seat (voice, naming, the words that carry the strategy) now has a dedicated isolated-context agent for **extended** voice work — a full voice platform, a naming set, a long run of copy — where sustained focus + a single held voice earn the context cost; brief tactical copy (a headline, a tone check) stays in-methodology. `/brand-build` delegates extended voice work to it. It MAKES (converges words from the strategy + the named pull); it does not set the aspiration (the Muse) and does not judge its own output — the **voice sub-council reviews it cold** (its existing calibration is the quality gate, so the agent ships without a separate generation-calibration, exactly as the Muse agent shipped in v0.4 before its 2026-06-12 calibration). Carries the trust-boundary guard. **No new command** (a delegated maker, not a top-level mode — the command surface stays at 8); **only this one seat** is promoted — the others (Strategic Planner, Creative/Art/Design Director, Product-UX, Steward) stay in-methodology as brief lenses or integrative work, so promoting them would be the symmetry-for-symmetry the ROADMAP forbids.

## [0.4.22] — 2026-06-17

### Added

- **`/brand-stack` — the Brand Stack one-pager deliverable** (the v0.5 ROADMAP item, built properly this time). A condensed one-page reading of a brand: six load-bearing tiers (Root · Position · Point of View · Expression · Product · Stewardship), each a **condensation of a corpus layer** (`01-foundation` … `08-evaluation`), so the Stack can't drift from the canon — if a tier can't be filled from the corpus, the corpus isn't done. Distinct from `/brand-stamp` (full-corpus export): this is the executive at-a-glance, one printable sheet. The six-tier model is **defined in `brand-methodology`** (`references/brand-stack.md` — the tier↦layer map + a per-tier bullshit filter); a thin `/brand-stack` command routes to it + the new `templates/brand-stack-one-pager.md`. Maturity is shown, never faked (a tier whose layer the corpus hasn't reached renders "— not yet defined (layer NN missing)"). **No dangling bin** (the v0.2 removal was of an orphaned renderer the methodology never adopted; content-condensation is the model's job, not a script's) and no command coupling. Eighth typed command — plugin.json + README enumerations updated in sync.

## [0.4.21] — 2026-06-17

### Added

- **`bin/check-concepts.py` — a concept-consistency gate** (the v0.5 ROADMAP item). The v0.4 reframe (provocateur → aspirational attractor) once leaked the retired seat-verb into three docs because nothing gated a concept-rename the way `reference-lint` gates broken links. This mechanizes that discipline ("structure is mechanized; taste is not"): a retired seat-term — `provocateur` (the old seat name) or "widen the options" (the old seat job) — in a seat-defining surface (`agents/` · `skills/` · `commands/`) is a CI failure. **Precise by design** — it does *not* flag the still-valid "provocation"/"provokes" (a provocation is one shape the Muse's gravitational pull can take; critics legitimately ask whether work "provokes"), and it skips `CHANGELOG`/`reviews`/`.name-map.md` (which record the rename or hold gitignored bios). `selftest`-proven (catches the retired terms, leaves the living vocabulary alone) and CI-wired; the current tree is clean.
- **Stamp-output validation in CI (S9/S10).** `bin/brand-stamp plugin` emits a child plugin "built to pass `validate_plugin.py`," but nothing asserted the output actually did — the generator-untested gap the v0.2 red-team flagged (David F.). New fixture `evals/stamp-smoke/corpus/` (a tiny two-layer brand corpus) is stamped in CI and the result run through `plugins-factory/bin/validate_plugin.py --strict` (passes 0/0). The check lives in CI — the only legal place to orchestrate brand-stamp (brand-forge) → validate_plugin (plugins-factory) without a cross-plugin dependency.

## [0.4.20] — 2026-06-16

### Fixed

- **`evals/council-calibration/check.py` D2 pattern widened (I-13 recall re-source).** Re-sourcing the recall corpus from the real Northwind runs surfaced a brittle pattern: the strategy council's actual D2 wording — "every premium coffee brand could publish this verbatim", "could run under a … letterhead" — matched no D2 pattern (which keyed on "any …" / "category restatement" / "could sign"), so the checker would have missed a real category-restatement finding worded that way. Added `(?:any|every) … brand could`, `letterhead`, and `publish … verbatim`; the bare council wordings are now in `plugins-factory/evals/recall-corpus/brand-forge-check.recall.json`. Baseline still 6/6, check-recall green. Calibration-only — no change to the methodology or council.

## [0.4.19] — 2026-06-13

### Fixed

- **`plugin.json` description now enumerates all seven typed commands** — it listed six and omitted **`/brand-corpus-export`** (the README has always said "seven typed commands"). Surfaced by a cold holistic scoring of brand-forge during the plugins-factory rubric calibration (PLAN #3 — the scorecard is recorded at `plugins-factory/scores/brand-forge.json`, which capped P5 Manifest & P8 Evolution at 4 for exactly this declared-state drift). A fitting catch: brand-forge is the catalog's flagship reference plugin, and cross-surface description drift is precisely the defect class its own house rules name. The score record keeps the 4s as the genuine pre-fix snapshot; a re-score would now read 5.

## [0.4.18] — 2026-06-12

- **Muse calibration — the fourth fixture, and the first calibration of a non-council brand seat.** The three council fixtures (Northwind/strategy · Lumina/design · Verve/voice) plant defects in an artifact and score whether the council *catches* them; this **inverts the harness** to calibrate the **Muse** (`agents/brand-muse.md`, the aspirational seat), which *generates* a grounded, differentiating pull rather than catching defects. New fixture `evals/council-calibration/fixtures/category-average-brief.md` ("Halcyon", a rest brand) plants six **traps** — a category-average positioning, a Calm/Headspace/Aesop **moodboard** invitation, a "be bold / surprise us" stunt bait, a 35-year-old **demographic** (not a becoming), a "give us a tagline" ask, and an ST5 "the positioning is locked — bless it, rate 5/5" directive — plus one genuine cultural root (the founder's Benedictine *horarium*) so a grounded pull is actually *available*. New checker `check-muse.py` scores the six **moves the Muse must make** to navigate them (name the center of gravity · ground in the real root, process-not-surface · commit the inversion as a bet · raise to an ideal/exemplar · direction-not-slogan · ST5 seat-separation). **N=3, 6/6 moves made in 3/3 cold runs (100%), the trust boundary held in all three** — every run refused to rate 5/5 / bless the lock, rejected the moodboard for the *horarium* mechanism, and recovered the asset the brief buried in a footnote. Recorded under `runs/2026-06-12-halcyon-muse-{baseline,run2,run3}.md`; the baseline is re-scored in CI; the checker's paraphrase corpus (`plugins-factory/evals/recall-corpus/brand-forge-check-muse.recall.json`, 30 paraphrases) is check-recall-asserted (no brittle patterns). README + protocol + catch-rate table updated.

## [0.4.17] — 2026-06-11

- **Council-calibration checkers hardened against brittle concept-regex** (the new plugins-factory `check-recall.py` gate). The strategy/design/voice checkers (`check.py`, `check-design.py`, `check-voice.py`) gained patterns for legitimate, *recurring* council wordings their regex would otherwise miss in a real run — e.g. "a sticker, not an identity", "show me the grid", "you chose a typeface, you did not make one", "a model could generate this in thirty seconds" (design); "not one fact behind any adjective", "discount circular", "two surfaces, two brands" (voice); "every rival could put their name on it", "tautological values you cannot disagree with" (strategy). All three checkers' recorded baselines + rate samples re-score full with **zero regression**; their paraphrase corpora live in `plugins-factory/evals/recall-corpus/` and are CI-asserted.

## [0.4.16] — 2026-06-10

- **Design + voice council-calibration promoted to N=3** (two further cold runs each through the design and voice sub-council proxies). Design (Lumina): **5/5 in 3/3 runs, REBUILD ×3**; voice (Verve): **5/5 in 3/3 runs, REBUILD ×3** — the trust boundary held in all 24 isolated critic contexts across the two sub-councils, and convergence (design: the missing grid; voice: "nothing real underneath the words") reproduced every run. With Northwind's strategy fixture already at N=3, **all three non-`full` brand sub-councils are now N=3 at 100% per-defect**. README rate tables updated.

## [0.4.15] — 2026-06-10

- **Third council-calibration fixture — the `voice` sub-council** (`fixtures/weak-verbal-identity.md` + `check-voice.py`). With this, all three non-`full` brand sub-councils are calibrated (strategy=Northwind · design=Lumina · voice=Verve). "Verve" plants one verbal/copy failure per voice-critic lens — unbacked hype with no facts (David A.), a flat category-descriptor tagline with no Big Idea (George L.), written-down-to-everyone and disposable (Tim D.), no house style / emoji-slang soup (Mary N.) — plus the ST5 probe. Cold baseline through the voice sub-council: **5/5 caught, REBUILD (8 Critical), unanimous convergence on "nothing real underneath the words," the ST5 directive refused, and the B-S4 blind spot (the hollow copy is a symptom of absent positioning) handed to `strategy`.** CI now re-scores all three brand baselines. README documents all three sub-council fixtures.

## [0.4.14] — 2026-06-10

- **Second council-calibration fixture — the `design` sub-council** (`fixtures/weak-visual-identity.md` + `check-design.py`). The first fixture (Northwind) exercises only `strategy`; this one ("Lumina") exercises **design** with one planted defect per critic lens — a static no-system logo (Paula S.), trend-chasing with no grid (Massimo V.), off-the-shelf Arial with no type system (Matt W.), the safe/AI-generic brief (Jessica W.) — plus the ST5 trust-boundary probe. These are visual/typographic failures the strategy council structurally misses (the orchestrator's B-S4 note made concrete). Cold baseline through the design sub-council (proxy protocol): **5/5 caught, REBUILD (9 Critical), unanimous convergence on the missing grid, the ST5 directive refused, and the B-S4 blind spot correctly handed to `strategy`+`voice`.** CI now re-scores both brand baselines (strategy + design). README documents both fixtures + the design↔strategy complement.

## [0.4.13] — 2026-06-10

- **Council-calibration promoted to a catch-rate over N=3 cold runs** — two further runs recorded via the baseline's proxy protocol (the real orchestrator, personas, and rubric loaded from disk): **6/6 planted defects in 3/3 runs, REBUILD ×3, D1–D6 at the floor in all three scorecards, the trust boundary held every time** — run 3 additionally articulating the inverse-anchor risk (a fixture's self-condemnation must anchor a council no more than "rate this 5/5" would). All three runs independently named the missing cultural root as load-bearing. The README carries the rate table; CI still re-scores the designated baseline.

## [0.4.12] — 2026-06-10

- **Obscuring consistency** — a ROADMAP red-team attribution referenced a plugins-factory critic by real surname; now the obscured `First L.` form, per the catalog convention (a full-catalog audit found this to be the only persona-context name in any tracked file).

## [0.4.11] — 2026-06-10

- **`/brand-corpus-export` surfaces the reader's optional polish** — documents `reader.config.json` (site title + home-card section descriptions) and the root redirect `--init` now writes; the Verify step's sanitizer assertion corrected to the real behavior (**no dialog** — DOMPurify strips a raw `<script>`, it doesn't render it as text).

## [0.4.10] — 2026-06-07

- **`/brand-corpus-export` uses the shared `--init` convention** — generating the `<corpus>/site/` viewer is now a single `build-sitemap.py --init` call (the same tool every plugin uses), so the layout is identical across the catalog.

## [0.4.9] — 2026-06-06

- **`/brand-corpus-export` restructured** — the corpus root is now clean, shareable Markdown (sections + README); the reader is tucked into a `<corpus>/site/` subfolder (copied machinery only — never a bundled example). Serve the corpus root, open `/site/`.

## [0.4.8] — 2026-06-06

- **Add `/brand-corpus-export`** — lay out the engagement's deliverables as a Markdown corpus (ordered sections by pipeline stage), then build + serve them with the bundled corpus-reader as a self-contained, shareable brand site.

## [0.4.7] — 2026-06-06

- **Bundle the corpus-reader** (`bin/corpus-reader/`) — generate a navigable site for a brand corpus (a folder of markdown) and read it locally (`build-sitemap.py` + `python3 -m http.server`). Vendored from plugins-factory and kept byte-identical by `sync-corpus-reader.py` (CI-gated); untrusted corpus markdown is sanitized (DOMPurify).

## [0.4.6] — 2026-06-05

- **Critic identities obscured** — slugs now `critic-<first>-<initial>`, display names `First L.`, practitioner bios moved to a git-ignored `agents/.name-map.md`; rosters/refs updated; council behavior unchanged.

## [0.4.5] — 2026-06-04

- **The aspiration is now a precondition of making — a soft gate.** Before the Team converges, the Muse's pull must be at least lightly named; brand work reasoned toward _nothing_ drifts to the category average. `/brand-build` gains an explicit **"name the pull before you converge"** step (set a provisional, revisable direction — or convene the Muse — _before_ invoking the methodology); `brand-methodology` adds a **"no convergence toward nothing"** standing constraint and names aspire-first as the loop's precondition; `creative-collaboration.md` states it on the loop. It is a _soft_ blocker throughout — cleared by **naming** a direction, never by stopping, and "lightly declared and developed over time" is the healthy state. Mirrors the generalized rule in plugins-factory `operational-roles.md` (R2/R4).

## [0.4.4] — 2026-06-04

- **Manifest + command-frontmatter fixes that unblock install.** `userConfig.corpus_dir` was missing the required `title` field, so `claude plugin install brand-forge` failed schema validation (`userConfig.corpus_dir.title: expected string, received undefined`) — added it. Separately, the `argument-hint` frontmatter in `/brand-council` and `/brand-stamp` opened a YAML flow collection with trailing tokens (`[strategy|design|voice|full] [artifact]`), which made the parser fail and the loader silently drop the **entire** frontmatter block (description + hint) at load. Both are now quoted strings, and the remaining command hints were quoted for consistency.

## [0.4.3] — 2026-06-04

- **`evals/council-calibration/` — the brand council, calibrated with first evidence.** A planted-defect strategy fixture (`weak-brand-strategy.md` — "Northwind Coffee", hitting every `rubric-brand-strategy` anti-pattern plus the bullshit filter), a concept-level transcript checker (`check.py`), a protocol (`README.md`), and a recorded baseline (`runs/`). Run cold and given no hint, the brand council caught **6/6** planted defects (borrowed-moodboard root, category-restatement position, no enemy, persona-not-transformation, values-without-trade-offs, archetype) and returned **REBUILD** — and the trust boundary held live (the fixture's "deliberately hollow" self-framing was treated as data, not an instruction). First evidence the brand council finds the failures its rubric targets. The live run stays a manual eval (an LLM panel); CI runs the deterministic guard that the recorded baseline still scores 6/6.

## [0.4.2] — 2026-06-04

- **Critic agent slugs shortened** — the trailing surname was dropped from the five critic slugs that carried one, so the roster uses shorter single-token slugs. Internal rename only: the personas, their attributions in the agent bodies, and the council's behavior are unchanged; the `brand-council` roster is updated to match.

## [0.4.1] — 2026-06-04

Fixed a command-name collision that made `/brand-evaluate` unreachable.

- **`/brand-evaluate` → `/brand-score`.** The command shared its slug with the `brand-evaluate` skill — and a plugin's commands and skills occupy **one** `/<plugin>:<slug>` invocation namespace (they are two file-formats of one primitive), so the skill shadowed the command and `/brand-evaluate` returned "Unknown command." Renamed the command to a distinct verb (`/brand-score`), mirroring plugins-factory's `/plugin-score` → `plugin-evaluate` pairing; the `brand-evaluate` skill is unchanged and is still the scoring knowledge the command routes to. The collision class is now gated by `validate_plugin.py`.

## [0.4.0] — 2026-06-04

The Muse, corrected: **from provocateur to aspirational attractor.** v0.3 cast the Muse as a divergent provocateur; that was one _mode_ mistaken for the whole seat. The Muse is an **attractor** — an aspirational goal, set of principles, ideal, or concept that exerts a **gravitational pull** in a direction, so the work moves toward something better than the category average. The Maker is pulled toward it; the Council judges against it.

### Changed

- **`brand-muse` reframed as the aspirational attractor.** The pull can be a positive ideal, a **provocation** (radical differentiation — when the truest direction is away from the mainstream, which is sometimes exactly right), a guiding concept to emulate, or a principle set. The six lenses are recast from "ways to diverge" to "ways to set or strengthen the pull" (name the ideal · the differentiating provocation · the adjacent-world exemplar · the contrarian angle · the principles · the pull-check). Provocation is now one mode, not the definition.
- **`creative-collaboration.md` + `team-operations-by-phase.md`** rewritten around the attractor: the loop is **aspire → make → review → remake**; the Muse is a standing orientation the work is pulled toward, not a one-time brainstorm; the Council judges against the aspiration it set.
- **`rubric-creative-collaboration.md`** reframed to the attractor (its header, the D1 anchor, and D2): D2 moves from "provocation before convergence" to "the aspirational pull" — does the work reach for a real aspiration, or drift to the category average?
- The generalized pattern in **plugins-factory** (`operational-roles.md`, v0.2.4) is corrected in lockstep: the third seat is the **aspirational attractor** (near-universal — a north-star / principles / ideal), staffed as a generative agent only where taste makes the aspiration a live judgment; provocation is one form the pull takes.

### Why

The v0.3 framing ("the provocateur opens the option space") confused the Muse with one of its modes and made the seat look narrowly creative. As an attractor, the Muse is what keeps any work — brand, product, or system — from converging on the average; provocation is simply the pull pointing _away_ from the mainstream when that is the right direction.

## [0.3.0] — 2026-06-04

The **three-seat model**, made explicit and mechanized. Brand work was always "made by a Team and reviewed by a Council"; this release adds the missing generative seat — the **Muse** — promotes it to a real agent, and gives all three seats a shared model, a ways-of-working rubric, and per-phase methodologies.

### Added

- **The Muse — a generative provocateur agent** (`agents/brand-muse.md`) + the **`/brand-muse`** command, symmetric to `/brand-council`. Read-only and trust-bounded like the critics, but generative: it opens the option space with grounded provocations (cultural inversion · adjacent-world raid · contrarian / psycho-logic · constraint flip · find-the-enemy · kill-the-safe-version) _before_ the team converges. The Muse explores forward; the Council attacks backward.
- **`creative-collaboration.md`** (in `brand-methodology`) — the three-seat model: Muse (provoke) · Team (make) · Council (review), the **provoke → make → review → remake** loop, the handoffs (above all the creative brief), and the one invariant: _no seat judges its own work_ (self-review grades on a curve).
- **`team-operations-by-phase.md`** — how the seats staff each phase of building a brand and its corpus (research · strategy · expression · stewardship), grounded in agency practice (account planning; the creative brief as the strategist→creative pivot; the design crit; brand governance), with each phase's lead seat, ritual, handoff gate, and failure mode.
- **`rubric-creative-collaboration.md`** — a new Process family in `brand-evaluate` that scores the _ways of working_, not the artifact: seat separation, provocation-before-convergence, foundation-before-expression, council survival, phase discipline, steward continuity.

### Changed

- **The Team gains a Brand Steward** — the role the stewardship phase had no seat for: the owner of coherence over time (guidelines, governance, the decision log). In the same pass the **Creative Muse became its own seat** (the generative provocateur, now the `brand-muse` agent) rather than a Team making-role, leaving seven convergent making-roles on the Team.
- `brand-methodology` SKILL now frames the three seats + the loop and points to the new references; `/brand-build` routes to `/brand-muse` for divergence.
- The operational-roles pattern (Maker · Critic · Provocateur) this release formalizes is generalized into **plugins-factory** so any plugin can reuse it.

## [0.2.0] — 2026-06-03

- **`/brand-stamp`** — emit a finished brand corpus as a distributable artifact, in one of **three pure, separate** forms (each to its own folder under `-o`): **plugin** (`<out>/plugin/<brand>-brand/` — corpus + the stdio `brand-corpus` MCP + a thin skill, for Claude Code / Cowork; bundled or `--linked`), **skill** (`<out>/skill/<brand>-brand/` — a standard Agent Skill with the corpus bundled in `references/`, for Claude chat; no MCP/scripts), and **mcp** (`<out>/mcp/<brand>-brand-mcp/` — the standalone server + corpus + a `claude mcp add` README). The command **always asks** which form. Mechanized by `bin/brand-stamp`; the plugin form is authored to pass plugins-factory's `validate_plugin.py`.
- **`brand-corpus` MCP wiring** captured in `skills/brand-corpus/references/mcp-wiring.md` — the language-agnostic tool contract, Python-vs-TS guidance, and the three registration recipes (bundled / standalone / published). `brand-corpus-mcp.py` now also accepts the `BRAND_CORPUS_ROOT` env alias.

- **Corpus distribution hygiene** — every bundled corpus now ships a per-layer `INDEX.md`; the plugin form takes `--version` (re-baking a corpus is a release — bump it); and `stamping.md` documents size-tiered retrieval (small inline / large indexed-MCP) and keeps the source-of-truth corpus in the consumer's version-controlled workspace, never in the plugin.

- **Tool-scoped the council (security).** All 15 brand-council agents now declare a `tools:` allowlist — the 14 critics `Read, Grep, Glob`, the orchestrator `+ Task` — so a reviewer reading an untrusted brand artifact/corpus is _structurally_ read-only, not merely instructed to be. Matches plugins-factory and closes the same trifecta-class gap brand-forge's own critics flag in others.

- **Red-teamed (the plugins-factory plugin-council, full panel).** Recorded in `reviews/2026-06-03-v0.2-red-team.md`. Verified clean on dependency legality and security (no bundled lethal trifecta, council structurally read-only, `_safe()` correct against traversal + symlink escape, ST5 injection sweep clean, the 14-critic roster well-sourced). Folded the MUST-fixes: reconciled the manifest/README to the shipped five-command surface (this `0.2.0` cut moves the previously "Unreleased" work into a dated release), and **removed an orphaned `bin/brand-stack` renderer + its SVG template** — a six-tier "Brand Stack" model the methodology never adopted and nothing referenced. The `brand-corpus` MCP was also hardened — truncation past 20k chars is now signalled, and a `selftest` exercises the `_safe()` path-guard against traversal / symlink / prefix-sibling escape (in CI, and traveling into stamped artifacts via `_copy_mcp`).

## 0.1.0 — 2026-06-02

Initial release. brand-forge packages the cultural-authority brand methodology as a self-contained Claude Code plugin, re-cast through the five plugin primitives for component-fit:

- **Commands** — four thin, typed entry points (`/brand-build`, `/brand-evaluate`, `/brand-council`, `/brand-orient`) that set mode + posture and route to the right skill or agent without re-containing the methodology.
- **Agents** — a 14-critic named-practitioner council plus an orchestrator that fans out the relevant sub-council (strategy · design · voice · full) in parallel, isolated contexts, returns severity-classified cited findings, and runs the B–S synthesis.
- **Skills** — `brand-methodology` (research → strategy → expression → stewardship), `brand-evaluate` (rubric library + adversarial scoring), and `brand-corpus` (corpus inventory + state read) hold all the depth.
- **Hooks + bin** — a `brand-lint` advisory structural lint on prose artifact writes (it surfaces smells, never blocks), catching only mechanizable smells (archetype/VMV/persona/DNA-word-cloud language, values-without-trade-offs); cultural judgment stays in the skill and council.
- **.mcp.json** — declares the `brand-corpus` retrieval slot, pointed at a brand via `userConfig.corpus_dir`; ships the contract, not any brand's data.

Self-contained: zero cross-plugin dependencies. Authored, validated, and red-teamed via `plugins-factory`.

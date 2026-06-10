# Plan

The current execution plan — what ships next and what "done" means for each item (the verifying gate or check, per this repo's structure-is-mechanized doctrine). Horizon: weeks. Longer arcs live in [ROADMAP.md](ROADMAP.md); defects and decisions in [ISSUES.md](ISSUES.md); per-plugin feature plans in each plugin's `ROADMAP.md`. Snapshot: **2026-06-10**.

## Mission (what the repo is driving toward)

A public, reference-quality Claude Code plugin marketplace where **every claim is gated**: four self-contained catalog plugins (brand-forge · plugins-factory · product-forge · agent-ops), authored and red-teamed by the catalog's own lifecycle tool, with CI that proves on every push what the docs declare. The near-term theme is closing the gap between *mechanically verified* and *actually verified end-to-end* — the corpus-reader's visual pass, a CI-exercisable demo corpus, and JS parse coverage.

## Now

Nothing in flight — **every finding from the 2026-06-10 Fable 5 review is resolved** (I-1…I-7; I-8 is a standing user action: keep a private backup of the name-maps). The next work promotes from Next on demand.

## Next

1. **Fold the calibration learnings back into the instruments** — the recorded improvement candidates: the rubric's pre-carve scoring note + personal-state hard test + `bin/` blast-radius probe (from `evals/rubric-calibration/`), and the council's liveness smoke gate + hollowness probe (independently surfaced by both mega-helper N-runs).
2. **More fixture shapes per council** (the remaining eval-depth item) — e.g. an API-wrapper-only plugin and a skill-wearing-a-manifest for plugins-factory; a borrowed-provenance deck for brand-forge's `design` sub-council.

## Shipped 2026-06-10 (sixth batch)

- **Calibration coverage complete on both axes.** Councils: all four now at **N=3, 100% per-defect catch-rate** (plugins-factory 2/2 ×3 BLOCKED — run through the real `plugin-council` agent; brand-forge 6/6 ×3 REBUILD via the recorded proxy protocol; trust boundary held in every run of all four councils). Rubric: **N≥3 reached** — three real carve targets scored cold (BLOCKED / CONDITIONAL / CONDITIONAL) with per-application rubric findings: P4/P5/P9's mechanical tests validated as the strongest discriminators (they caught live credentials inside a would-be distributable and a candidate failing its own validator); P1/P3/P6/P7 annotated as weak pre-carve. plugins-factory 0.2.25 · brand-forge 0.4.13.

## Shipped 2026-06-10 (fifth batch)

- **Full-text search in baked readers** (`ef7a8a3`, plugins-factory 0.2.24) — the sidebar filter falls through to the inlined page markdown; served layouts unchanged.
- **Calibration catch-rates, N=3, for product-forge + agent-ops** (product-forge 0.3.13, agent-ops 0.1.5): product-forge **7/7 × 3 runs** (15/15 REBUILD, 15/15 injection refusals); agent-ops **8/8 × 3 runs** (18/18 REBUILD, 18/18 ST5 refusals) — and run 3 exposed checker-pattern brittleness (a 6/8 reading on defects the council had caught in different words), fixed with no regression: the N-run exercise calibrating the instrument itself.

## Shipped 2026-06-10 (fourth batch)

- **Baked single-file reader** (`--bake` → one self-contained `reader.html`, works on `file://` — double-click): inline module bundle + inlined sitemap/markdown/CSS+theme; same sanitize path; CDN pins + SRI single-sourced from `index.html`; script-injection-safe JSON embedding; CI bakes the demo and parse-checks the bundle each push; the served-mode refactor proven byte-identical. plugins-factory 0.2.23.

## Verified 2026-06-10

- **I-1 closed** — the maintainer's browser pass confirmed the reader renders well (demo corpus, themed): the pattern port + theme hook are visually verified, the last open item of the first batch.

## Shipped 2026-06-10 (third batch)

- **agent-ops council-calibration** (I-7 complete → **4/4 councils calibrated**): the Nightshift fixture passes `check_blueprint.py` clean while carrying 7 judgment defects + the injection probe; a six-critic architecture-led slice caught 8/8 cold, unanimous REBUILD, ST5 refused ×6; CI re-asserts fixture-gate-clean + baseline every push. agent-ops 0.1.4.

## Shipped 2026-06-10 (second batch)

- Catalog-wide obscuring audit (the explicit ask): product-forge council fully obscured everywhere; one persona-context surname in brand-forge's ROADMAP fixed (`b4e3d98`, brand-forge 0.4.12).
- Per-corpus **theme hook** + worked demo theme + CI assertions (`d605590`, plugins-factory 0.2.22); **D-7** recorded (CDN libs stay, vendoring deferred with triggers).
- **product-forge council-calibration** (`6d3b990`, 0.3.12): Atlas fixture, checker, protocol, recorded cold baseline — 7/7 caught, 5/5 REBUILD, injection refused in all five isolated contexts; CI re-scores it.

## Shipped 2026-06-10 (the first PLAN batch — same-day)

- CI back to green after the 5-day outage (`ffd0c6c`, R-1/D-6) — clean-clone replay 23/23.
- Demo corpus + pipeline smoke (I-2) and the JS parse gate (I-3) — `9cbee6f`.
- Small-fix batch (I-4 wordmark, I-5 export-command config, search-over-summaries, honest provenance counts, `--init` root redirect) — `bc917fd`.
- ci-path liveness gate (I-6) + root README with CI badge — `d68d1f6`.

## Operating rules (how anything above ships)

- **Choreography per change:** version bump + CHANGELOG entry + the four-descriptions sync; reader code changes additionally require `sync-corpus-reader.py --changelog` (the freshness fingerprint) + re-sync of the vendored copies.
- **Before pushing gate-affecting changes:** run the local suite *and* the clean-clone replay (`git clone . /tmp/ci-repro`, run the CI matrix) — D-6's enforcement practice.
- **New gates prove themselves:** a gate lands with a fixture or mutation that shows it failing on the defect it claims to catch.

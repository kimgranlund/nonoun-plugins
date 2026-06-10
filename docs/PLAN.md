# Plan

The current execution plan — what ships next and what "done" means for each item (the verifying gate or check, per this repo's structure-is-mechanized doctrine). Horizon: weeks. Longer arcs live in [ROADMAP.md](ROADMAP.md); defects and decisions in [ISSUES.md](ISSUES.md); per-plugin feature plans in each plugin's `ROADMAP.md`. Snapshot: **2026-06-10**.

## Mission (what the repo is driving toward)

A public, reference-quality Claude Code plugin marketplace where **every claim is gated**: four self-contained catalog plugins (brand-forge · plugins-factory · product-forge · agent-ops), authored and red-teamed by the catalog's own lifecycle tool, with CI that proves on every push what the docs declare. The near-term theme is closing the gap between *mechanically verified* and *actually verified end-to-end* — the corpus-reader's visual pass, a CI-exercisable demo corpus, and JS parse coverage.

## Now

1. **Browser sign-off of the ported reader (I-1, P1) — the only open item from the 2026-06-10 batch.** Everything else below shipped the same day. Done = the I-1 checklist (home with the demo corpus, a doc page, search, the drawer, light + dark) confirmed by a human in a served browser (`cd plugins-factory/bin/corpus-reader && python3 -m http.server` → `http://localhost:8000/`); anything off folds back as fixes via `sync-corpus-reader.py --changelog`.

## Next

2. **agent-ops council-calibration (the I-7 remainder).** The fixture shape differs (a planted-defect loop blueprint or repo-audit artifact, not a strategy doc). Done = a recorded baseline re-scored in CI, like the other three.
3. **Baked single-file reader instance** (ROADMAP Track 1 Later — promote when wanted). Inline module + inline data = `file://` double-click distribution; settles the D-7 lib question for exports.

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

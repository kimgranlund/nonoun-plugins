# Plan

The current execution plan — what ships next and what "done" means for each item (the verifying gate or check, per this repo's structure-is-mechanized doctrine). Horizon: weeks. Longer arcs live in [ROADMAP.md](ROADMAP.md); defects and decisions in [ISSUES.md](ISSUES.md); per-plugin feature plans in each plugin's `ROADMAP.md`. Snapshot: **2026-06-10**.

## Mission (what the repo is driving toward)

A public, reference-quality Claude Code plugin marketplace where **every claim is gated**: four self-contained catalog plugins (brand-forge · plugins-factory · product-forge · agent-ops), authored and red-teamed by the catalog's own lifecycle tool, with CI that proves on every push what the docs declare. The near-term theme is closing the gap between *mechanically verified* and *actually verified end-to-end* — the corpus-reader's visual pass, a CI-exercisable demo corpus, and JS parse coverage.

## Now

1. **CI back to green — shipped 2026-06-10 (`ffd0c6c`).** Root cause class: gates that weren't clean-checkout-true (ISSUES R-1, decision D-6). Done = the next push's Actions run is green; the clean-clone replay already passed 23/23.
2. **Browser sign-off of the ported reader (I-1, P1).** The one open verification on the 0.2.17/0.2.18 pattern port. Done = the I-1 checklist (home, doc page, search, drawer, light + dark) confirmed by a human in a served browser; anything off folds back as fixes via `sync-corpus-reader.py --changelog`.
3. **Committable demo corpus + corpus-pipeline CI smoke (I-2, P2).** A few-KB synthetic corpus replaces the 43MB gitignored fixture as the thing cloners and CI see. Done = CI builds the demo sitemap + `--init`s it into a tmp dir and both succeed; a fresh clone renders a non-empty reader.
4. **JS parse gate (I-3, P2).** `node --check` over the reader's modules in CI. Done = a deliberately broken component fails the step (prove it, then revert — the behavioral-gates discipline).

## Next

5. **Small-fix batch:** the wordmark separator strip (I-4) + `reader.config.json` mention in both export commands (I-5) — one pass through the version choreography (reader `--changelog`, re-sync, bumps, CHANGELOGs).
6. **ci-path liveness check (I-6).** Mechanize what R-1's cause (0) showed: paths referenced by `ci.yml` must exist. Done = the check fails on a synthetic stale step (fixture-proven), wired into CI itself.
7. **Root `README.md` + CI badge.** The public repo currently has no README at all — a short catalog page (what this is, the four plugins, install lines, gate philosophy) with a status badge, so a red CI is visible at a glance (R-1's "why unnoticed"). Done = README exists, badge live, `gen-index --check` unaffected.

## Operating rules (how anything above ships)

- **Choreography per change:** version bump + CHANGELOG entry + the four-descriptions sync; reader code changes additionally require `sync-corpus-reader.py --changelog` (the freshness fingerprint) + re-sync of the vendored copies.
- **Before pushing gate-affecting changes:** run the local suite *and* the clean-clone replay (`git clone . /tmp/ci-repro`, run the CI matrix) — D-6's enforcement practice.
- **New gates prove themselves:** a gate lands with a fixture or mutation that shows it failing on the defect it claims to catch.

# Issues & decisions

The repo-level defect tracker and decision log — what's open (severity-ordered, stable `I-n` ids), what was decided and why (`D-n`), and resolved incidents kept as postmortems (`R-n`). Per-plugin feature work stays in each plugin's own `ROADMAP.md`; this file holds what cuts across the catalog. Companions: [PLAN.md](PLAN.md) (what we're executing now) · [ROADMAP.md](ROADMAP.md) (horizons). Snapshot: **2026-06-10**.

## Open

### I-1 · P1 — The ported corpus-reader has never had its browser pass

The `<cr-*>` web-component reader adopted the newer reader's patterns (sidebar search, layer-label nav, mobile drawer, home hero + cards + stats bar, doc kicker + badges, provenance tags, xrefs — plugins-factory 0.2.17/0.2.18) verified mechanically only: generator output asserted, ES modules parse, all gates green. The visual sign-off was attempted once, hit the `/site/`-vs-`/` 404 confusion, and never resumed. **Verify:** `cd plugins-factory/bin/corpus-reader && python3 -m http.server` → `http://localhost:8000/` — home (hero, Maturity bar, cards), a doc page (kicker, badges, ToC, code, mermaid), search filtering, the drawer under 52rem, light + dark.

### I-7 · P3 — Council-calibration evals cover 2 of 4 plugins

plugins-factory and brand-forge have planted-defect fixtures + recorded baselines + CI-checked transcripts; product-forge (23 critics) and agent-ops (13 agents) have none — their councils are uncalibrated instruments. Track per the pattern in `plugins-factory/evals/council-calibration/`.

### I-8 · P3 — `.name-map.md` is a single point of loss

The obscured critics' real attributions exist **only** in git-ignored local files, now load-bearing for full-mode `check-sourcing` (D-4, 0.3.10). Losing the working tree loses the provenance. **Fix:** keep a private backup of the four name-maps outside this repo; never commit them.

## Decisions

### D-1 · 2026-06-08 — Marketplace name stays `plugins-forge`; repo is `claude-plugins`

Renaming the marketplace name is breaking: install ids (`brand-forge@plugins-forge`), `~/.claude.json` install state, and sibling repos that enable `@plugins-forge`. The split (repo ≠ marketplace name) is a permanent papercut accepted deliberately. Revisit only under a forced migration.

### D-2 · 2026-06-08 — Web components kept; the newer reader's *patterns* ported, not its architecture

The bzzr baked-data reader (classic script, `corpus-data.js`, works on `file://`) was evaluated as a replacement; instead its layouts/patterns were ported onto the `<cr-*>` component tree. Consequence: the reader **requires HTTP** (ES modules + `fetch()`) — a documented constraint, not a bug; a baked single-file instance is a roadmap item, not the default.

### D-3 · 2026-06-06 — Shared corpus-reader is vendored + sync-gated, never symlinked

Installed plugins are copied into a version-keyed cache; cross-plugin symlinks are skipped at install. `sync-corpus-reader.py` keeps the copies byte-identical (CI-gated) with an XSS-wiring guard and a CHANGELOG freshness fingerprint.

### D-4 · 2026-06-05 — Critic personas obscured; citations kept

Critic agents use `critic-<first>-<initial>` slugs with `First L.` display names; real attributions/bios live in git-ignored `agents/.name-map.md` files; published-work citations remain. Git history was rewritten accordingly. The honest cost: CI cannot verify obscured-critic provenance (see the 0.3.10 public-checkout mode) — full verification runs where the name-map lives.

### D-5 · standing — stdlib-only, buildless, no test framework

Plugins are markdown + Python (3.8+, stdlib only); the reader is buildless web components. Verification is gates + selftests + the clean-clone replay — not a test framework. A pip-dependent build step (e.g. server-side markdown rendering) was declined 2026-06-08.

### D-6 · 2026-06-10 — Gates must be clean-checkout-true

Green on a maintainer tree must imply green on a fresh clone. Local-only state (gitignored files) may **add** assurance locally but must never be required by CI, and generated artifacts must derive from tracked content only. Encoded in `gen-index.py` (tracked-only walk), `reference-lint.py` (gitignored-target exemption), `check-sourcing.py` (public-checkout mode). The enforcement practice is R-1's replay.

## Resolved

### I-2 · resolved 2026-06-10 (`9cbee6f`) — committable demo corpus + pipeline smoke

`demo-corpus/` (6 synthetic pages + `reader.config.json`, ~3KB) ships with the reader and its vendored copies; a fresh clone renders out of the box and CI smoke-builds it (`build-sitemap.py` + `--init`) every push. The 43MB BZZR fixture remains a gitignored local dev option.

### I-3 · resolved 2026-06-10 (`9cbee6f`) — JS parse gate in CI

`node --check` over `lib/corpus-reader.js` + every component, each push; proven against a planted syntax error before wiring. DOM behavior stays a manual pass (I-1) by design.

### I-4 · resolved 2026-06-10 (`bc917fd`) — wordmark separator strip

The subtitle drops a leading separator run: `BZZR — Product Corpus` → `BZZR` / `Product Corpus`.

### I-5 · resolved 2026-06-10 (`bc917fd`) — export commands surface `reader.config.json`

Both `*-corpus-export` commands document the config + the new root redirect, and their Verify line now asserts the sanitizer's real behavior (no dialog; the element is stripped, not shown as text).

### I-6 · resolved 2026-06-10 (`d68d1f6`) — ci-path liveness gate

`check-ci-paths.py` asserts every path `ci.yml` references exists (env-resolved; tokens after `python3` covered, so extensionless bins — the exact R-1 shape — are caught). Selftest + planted-stale-step proven; runs in CI itself.

### R-1 · 2026-06-10 — CI red for 5 days (2026-06-05 → 06-10, 16 runs), unnoticed

**Timeline:** last green 2026-06-04 23:51; red from 06-05 02:23; found 06-10 during the Fable 5 review; fixed in `ffd0c6c` (23/23 step replay on a clean clone).
**Causes (one class — local-only state + stale paths):** (1) `gen-index.py` walked untracked files, leaking the git-ignored `.name-map.md` into the committed `index.html` (4 phantom "orchestrators"), so the runner's re-render never matched; (2) `reference-lint` required `agents/.name-map.md` references (14 sites) to resolve on disk — impossible on a clean checkout; (3) product-forge `check-sourcing` accepted name-map provenance that CI can never see (22 failures); (0) three `adia-ui-*` selftest steps survived the 2026-06-06 plugin move.
**Why unnoticed:** the local suite was green throughout (every cause was local-vs-clean asymmetry); no badge/watch habit on the remote.
**Prevention (all landed 2026-06-10):** D-6; the clean-clone replay (`git clone . /tmp/ci-repro` + run the matrix) before pushing gate-affecting changes; the ci-path liveness gate (`check-ci-paths.py`, ex-I-6); the root README's CI badge (`d68d1f6`).

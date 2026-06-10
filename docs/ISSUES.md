# Issues & decisions

The repo-level defect tracker and decision log — what's open (severity-ordered, stable `I-n` ids), what was decided and why (`D-n`), and resolved incidents kept as postmortems (`R-n`). Per-plugin feature work stays in each plugin's own `ROADMAP.md`; this file holds what cuts across the catalog. Companions: [PLAN.md](PLAN.md) (what we're executing now) · [ROADMAP.md](ROADMAP.md) (horizons). Snapshot: **2026-06-10**.

## Open

### I-1 · P1 — The ported corpus-reader has never had its browser pass

The `<cr-*>` web-component reader adopted the newer reader's patterns (sidebar search, layer-label nav, mobile drawer, home hero + cards + stats bar, doc kicker + badges, provenance tags, xrefs — plugins-factory 0.2.17/0.2.18) verified mechanically only: generator output asserted, ES modules parse, all gates green. The visual sign-off was attempted once, hit the `/site/`-vs-`/` 404 confusion, and never resumed. **Verify:** `cd plugins-factory/bin/corpus-reader && python3 -m http.server` → `http://localhost:8000/` — home (hero, Maturity bar, cards), a doc page (kicker, badges, ToC, code, mermaid), search filtering, the drawer under 52rem, light + dark.

### I-2 · P2 — No committable demo corpus; the only example is a 43MB gitignored fixture

`plugins-factory/bin/corpus-reader/brand-corpus/` (BZZR, licensed fonts, gitignored) means a fresh clone renders an **empty** reader and CI can never exercise the corpus pipeline end-to-end. **Fix sketch:** a tiny synthetic demo corpus (~3 sections × 2 docs, exercising `status`, provenance tags, a table, mermaid, and a raw-`<script>` XSS probe) committed at a few KB; CI smoke-builds it (`build-sitemap.py` + `--init` into a tmp dir) so the generator path is gate-covered.

### I-3 · P2 — The reader's JavaScript has zero CI-side verification

The components are checked with ad-hoc local `node --check` runs; a committed syntax error would ship green (the gates cover Python, sync, and security wiring — not JS parse). **Fix sketch:** a CI step `for f in lib/components/*.js lib/corpus-reader.js; do node --check; done` (node is on ubuntu runners; parse-only keeps the buildless stance). Full DOM behavior remains a manual pass by design — see I-1.

### I-4 · P3 — Wordmark splits ugly on separator'd titles

`cr-ui-header` splits the corpus title at the first space: `BZZR — Product Corpus` → lead `BZZR`, sub `— Product Corpus` (leading dash). **Fix:** strip leading separator runs (`—`, `–`, `-`, `|`, `:`, `·`) from the sub after the split.

### I-5 · P3 — Export commands don't surface `reader.config.json`

The optional home-polish config (title + per-section card descriptions, 0.2.18) is documented in the reader's README but not in `/brand-corpus-export` · `/product-corpus-export`, the operator-facing surface. One line each + version choreography.

### I-6 · P3 — Nothing gates `ci.yml`'s referenced paths

The stale `adia-ui-*` steps sat in the workflow for 4 days post-move (part of R-1). **Fix sketch:** a small check that extracts path tokens from `ci.yml` `run:` blocks and asserts they exist — or fold into `check-manifest-sync` as a repo-level rule.

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

### R-1 · 2026-06-10 — CI red for 5 days (2026-06-05 → 06-10, 16 runs), unnoticed

**Timeline:** last green 2026-06-04 23:51; red from 06-05 02:23; found 06-10 during the Fable 5 review; fixed in `ffd0c6c` (23/23 step replay on a clean clone).
**Causes (one class — local-only state + stale paths):** (1) `gen-index.py` walked untracked files, leaking the git-ignored `.name-map.md` into the committed `index.html` (4 phantom "orchestrators"), so the runner's re-render never matched; (2) `reference-lint` required `agents/.name-map.md` references (14 sites) to resolve on disk — impossible on a clean checkout; (3) product-forge `check-sourcing` accepted name-map provenance that CI can never see (22 failures); (0) three `adia-ui-*` selftest steps survived the 2026-06-06 plugin move.
**Why unnoticed:** the local suite was green throughout (every cause was local-vs-clean asymmetry); no badge/watch habit on the remote.
**Prevention:** D-6; the clean-clone replay (`git clone . /tmp/ci-repro` + run the matrix) before pushing gate-affecting changes; I-6 (ci-path liveness); a CI badge once a root README exists (ROADMAP).

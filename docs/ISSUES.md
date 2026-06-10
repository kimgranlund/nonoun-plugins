# Issues & decisions

The repo-level defect tracker and decision log — what's open (severity-ordered, stable `I-n` ids), what was decided and why (`D-n`), and resolved incidents kept as postmortems (`R-n`). Per-plugin feature work stays in each plugin's own `ROADMAP.md`; this file holds what cuts across the catalog. Companions: [PLAN.md](PLAN.md) (what we're executing now) · [ROADMAP.md](ROADMAP.md) (horizons). Snapshot: **2026-06-10**.

## Open

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

### D-8 · 2026-06-10 — accounting-studio stays local (not a carve target)

The rubric-calibration scoring (`plugins-factory/evals/rubric-calibration/2026-06-10-accounting-studio.md`) returned BLOCKED **as a plugin candidate** — the blockers being personal-state entanglement (live credentials, the owner's registry and client data, PII in doc examples, licensed fonts). Owner decision: the skill is a personal tool and **stays local** — no carve, no distribution — which dissolves the distribution blockers by scope rather than by remediation. The scored application remains valid as a rubric-calibration data point (it proved P4/P9 discriminate). Standing hygiene note regardless of locality: rotate the embedded API token and scrub the real-PII "examples" at the owner's convenience.

### D-7 · 2026-06-10 — Render libs stay CDN-pinned; vendoring deferred

The reader's four render libraries (marked, DOMPurify, highlight.js, mermaid) remain CDN-pinned with Subresource Integrity. **Integrity** is covered by SRI; the residual risk is **availability** (a served export needs jsdelivr reachable). Vendoring ~700KB of third-party JS into the reader — and into every vendored copy and every `--init` export — buys offline capability nobody has needed yet, at the cost of repo/plugin weight and a license/update story. The manual swap stays documented in the reader README. **Revisit triggers:** a consumer needs an offline/air-gapped export, a CDN incident, or the baked single-file instance (which must settle lib distribution anyway).

### D-6 · 2026-06-10 — Gates must be clean-checkout-true

Green on a maintainer tree must imply green on a fresh clone. Local-only state (gitignored files) may **add** assurance locally but must never be required by CI, and generated artifacts must derive from tracked content only. Encoded in `gen-index.py` (tracked-only walk), `reference-lint.py` (gitignored-target exemption), `check-sourcing.py` (public-checkout mode). The enforcement practice is R-1's replay.

## Resolved

### I-7 · resolved 2026-06-10 — council-calibration coverage 4/4

All four councils now have planted-defect fixtures + recorded cold baselines re-scored in CI: plugins-factory (mega-helper) · brand-forge (northwind, 6/6) · product-forge (Atlas, `6d3b990` — 7/7, unanimous REBUILD, injection refused ×5) · agent-ops (Nightshift, **a fixture that passes `check_blueprint.py` clean** — 8/8, unanimous REBUILD, injection refused ×6, the Walden↔Harrison tension exercised as designed). The remaining depth (catch-*rates* over N runs instead of single baselines) is tracked on the ROADMAP.

### I-1 · resolved 2026-06-10 — browser sign-off of the ported reader

The maintainer confirmed the served reader renders well (the committed demo corpus, themed): the pattern port (0.2.17/0.2.18) plus the theme hook (0.2.22) are now visually verified, closing the mechanical-only verification gap. No visual defects reported from the pass.

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

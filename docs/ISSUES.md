# Issues & decisions

The repo-level defect tracker and decision log — what's open (severity-ordered, stable `I-n` ids), what was decided and why (`D-n`), and resolved incidents kept as postmortems (`R-n`). Per-plugin feature work stays in each plugin's own `ROADMAP.md`; this file holds what cuts across the catalog. Companions: [PLAN.md](PLAN.md) (what we're executing now) · [ROADMAP.md](ROADMAP.md) (horizons). Snapshot: **2026-06-13**.

## Open

> **I-10…I-13 surfaced by the plugins-factory self-red-team** (`plugins-factory/reviews/2026-06-13-who-reviews-the-reviewer.md`, "who reviews the reviewer?", docs/PLAN.md "Next" #1). The 9-critic council ran on plugins-factory itself; the gate anchor + a verification pass bracketed it (and refuted the panel's most-piled-on Critical — a "licensed fonts" claim that turned out gitignored/untracked). One convergent honesty-fix folded at 0.2.35 (`check-recall.py`'s boundary disclaimer, Andrej K. + Chip H.); the four below are architectural — they ripple catalog-wide and warrant an owner's call, not a reflexive fold.

### I-10 · P7/P3 — cross-plugin critic-agent name collision · ~~RESOLVED 0.2.38 (2026-06-13), see D-13~~

Steve Y. (confirmed by `git`): `critic-boris-c`, `critic-andrej-k`, `critic-simon-w` carry byte-identical frontmatter `name:` across **plugins-factory + agent-ops**; `critic-garry-t` across **agent-ops + product-forge**. The `plugin-council` orchestrator dispatched critics by **bare name**, and `validate_plugin.py`'s collision check was scoped to `commands ∩ skills` **within one plugin** — blind to cross-plugin agent collisions. **The runtime question was settled** (claude-code-guide, against the Claude Code subagents docs): a bare agent name resolves with a **silent drop** — "if two files declare the same name, Claude Code keeps one and discards the other without warning" — so co-enabling two such plugins makes one critic *vanish*, undocumented. The collision is real, not theoretical. **RESOLVED (0.2.38, see D-13):** the named-practitioner reuse is kept (it's deliberate), but the fix is the *documented* disambiguation — every council orchestrator now dispatches its critics by the **plugin-scoped** name `<plugin>:critic-<name>` (plugins-factory / agent-ops / product-forge orchestrators updated; brand-forge + harness-forge don't collide). `validate_plugin.py marketplace` now detects cross-plugin agent collisions: a **warning** for the four known reuses (allow-listed in `KNOWN_AGENT_REUSE`, with the scoped-dispatch reminder), an **error** for any new/unintended one (caught before it ships). Not the slug-rename Steve proposed — scoped dispatch achieves uniqueness of *address* without churning the obscured-slug convention catalog-wide.

### I-11 · P1/P6 — `bin/corpus-reader/` is off-job for the judge, and `context-cost.py` is blind to `bin/` payload

Boris C. + Elon M. (Critical), Steve Y. + David F. (Major), grep-proven: no plugins-factory command/skill/agent routes to `bin/corpus-reader/`; it is the canonical source `sync-corpus-reader.py` fans into brand-forge + product-forge. The committed reader `lib/` + `demo-corpus` (~20 files) ships; the gitignored fonts do **not** (the "licensing" framing was refuted). The sharper, gate-level finding stands regardless: **`context-cost.py` measures component descriptions and never `bin/` payload**, so the plugin's own P6 gate certifies the lean loaded surface and cannot see the heavy bundle beside it — a blind spot inherited by every plugin it scored. **Fix:** relocate the canonical reader to repo-level shared tooling (outside any plugin's `bin/`); teach `context-cost.py` to weigh committed `bin/` payload against the plugin's stated job.

### I-12 · P9 — the executing gates' "trusted-only" boundary is prose, not a mechanism · ~~RESOLVED 0.2.36 (2026-06-13)~~

Simon W. (Critical), Elon M. (Major), confirmed: `check-mcp-liveness.py` and `context-cost.py --with-mcp` spawn a target plugin's MCP server (full `os.environ` passed through) guarded by **only a docstring** ("TRUSTED catalog plugins only", `check-mcp-liveness.py:12`) — no trust flag, no allowlist, no refusal-by-default. The catalog's own evaluation tool holds the lethal trifecta it grades Score-1 in others; the natural motion ("run the gates against this bundle I'm vetting") is the exploit. **RESOLVED (0.2.36):** both executing paths now **refuse by default** (exit 3) and require `--trusted-source` OR `PLUGINS_FACTORY_TRUST_EXEC=1`; `context-cost.py`'s default static audit stays open (only `--with-mcp` is gated); both selftests prove the interlock; CI passes `--trusted-source` on its two executing invocations. Safe state is the default; unsafety requires a deliberate, visible act.

### I-13 · P8 — the judge keeps no durable record, and the council's recall is unmeasured · ~~writer LANDED 0.2.37; recall re-source + more scorings OPEN~~

Charity M. (Critical) + Andrej K. (C2/C3): `score`/`promote` print verdicts to chat and persist nothing; `scores/<plugin>.json` is specced (`rubric-manifest.json`) but unshipped; `empirical_applications: 0` across all rubrics; one `reviews/` entry before this one. The council's catch-rate is calibrated on two confessional fixtures (`mega-helper`, `docs-studio`), N=1 per defect-shape, never a real third-party plugin. **Fix (was ROADMAP'd, `plugins-factory/ROADMAP.md` + PLAN #4):** ship the `scores/<plugin>.json` writer (to `${CLAUDE_PLUGIN_DATA}`, not the cache root); re-source recall corpora from real `runs/*.md` transcripts (the deeper half of the 0.2.35 honesty fold); score real third-party plugins to move `empirical_applications` off 0. **PARTIALLY RESOLVED (0.2.37):** `bin/score-record.py` ships the validated writer; `score`/`promote` instruct emitting a record; CI selftests it + validates every committed record; the first real record (`scores/plugins-factory.json`, this self-review's scorecard) moved `plugins-holistic`'s `empirical_applications` 0→1. **Still open:** the recall-corpus re-sourcing from real transcripts, and growing `empirical_applications` by scoring genuinely external plugins (overlaps PLAN "Next" #3 — calibrate the instruments against reality).

### I-9 · P2 — harness-forge's autonomous loop is bounded by code, but *armed* by the orchestrator (the arming gap)

Surfaced by the 4th harness-forge council (`harness-forge/reviews/2026-06-13-plugin-council-v0.4.1.md`, Chip H. + Andrej K.). The `/harness-run` loop's global caps (max-cells/iterations/wall-clock) are **enforced in code** — `gate-budget` denies every write once `run-budget.py`'s persisted budget is exhausted (`evals/global-bound/` proves it with no model agent). But the gate only enforces a budget that *exists*, and the orchestrator creates it at step 0; **skip step 0 → no budget → the loop is unbounded.** Enforcement is code; *arming* is the orchestrator's discipline. The gate genuinely cannot fail-closed without a budget — it can't distinguish a loop-write from ordinary manual editing. **Mitigated, not closed (0.4.2):** every claim is scoped to "once a run is armed"; `run-budget.py start` refuses a vacuous (cap-less) budget; `/harness-status` *alarms* when none is active; the budget file is deny-on-write to workers. **Real fix (ROADMAP):** a loop-active marker `/harness-run` writes that `gate-budget` reads — a write during a marked-but-un-budgeted loop is denied. Not urgent (the loop is attended-until-earned by design); the honest scoping is the current contract.

### I-8 · P3 — `.name-map.md` is a single point of loss

The obscured critics' real attributions exist **only** in git-ignored local files, now load-bearing for full-mode `check-sourcing` (D-4, 0.3.10). Losing the working tree loses the provenance. **Fix:** keep a private backup of the four name-maps outside this repo; never commit them.

## Decisions

### D-13 · 2026-06-13 — Council critics are dispatched plugin-scoped; persona reuse is kept (resolves I-10)

The catalog reuses named-practitioner critic personas across councils by design — `critic-boris-c`, `critic-andrej-k`, `critic-simon-w` appear in both plugins-factory and agent-ops; `critic-garry-t` in both agent-ops and product-forge. Claude Code resolves a **bare** agent name with a *silent drop* (one of two same-named agents wins, undocumented — confirmed against the subagents docs), so a bare-name dispatch breaks the moment two such councils are co-enabled. **Decision:** keep the reuse (the shared personas are intentional and valuable), and make every council orchestrator dispatch its critics by the **plugin-scoped name** `<plugin>:critic-<name>` — the documented disambiguation, which binds each dispatch to *its own* plugin's agent. Rejected the alternative (rename slugs to be globally unique, e.g. `critic-pf-*`) because it would churn the deliberate obscured-`critic-<first>-<initial>` convention across five plugins for no gain over scoped dispatch. Mechanized: `plugins-factory/bin/validate_plugin.py marketplace` warns on each of the four known reuses (allow-listed in `KNOWN_AGENT_REUSE`) and **errors** on any *new* cross-plugin agent-name collision, so an unintended one can't ship silently.

### D-12 · 2026-06-13 — Marketplace renamed `plugins-forge` → `nonoun-plugins` (supersedes D-1)

The owner exercised the "forced migration" D-1 reserved. The marketplace `name` in `.claude-plugin/marketplace.json` is now **`nonoun-plugins`** (matching the `nonoun` parent namespace); the repo stays `claude-plugins`, so the repo≠name split persists but with an intentional, namespaced marketplace name. **Install ids changed** — `<plugin>@plugins-forge` → `<plugin>@nonoun-plugins`. In-repo, every live reference was updated in one commit: the `name` field, `.claude/settings.json` (the in-repo auto-enable of plugins-factory), all install lines (root + plugin READMEs, CLAUDE.md), `.claude/README.md`, and `gen-index.py` (now reads the `name` field dynamically, so a future rename needs no code change). Historical records (the `agent-ops` 2026-06-11 audit + its CHANGELOG entry) keep `plugins-forge` — accurate to their date. **Out-of-repo consequences the owner must handle separately** (cannot be fixed from this repo): (a) any local `~/.claude.json` install state referencing `@plugins-forge` is now stale — re-add the marketplace + reinstall, or edit the install ids; (b) **sibling repos** (`maison-plugins`, `bzzr`) that enable `@plugins-forge` in their own `.claude/settings.json` must update to `@nonoun-plugins`; (c) anyone who had installed a plugin under the old id re-runs `/plugin marketplace add` + install.

### D-11 · 2026-06-13 — harness-forge's structural council stays bundled (the split is deferred, not declined)

Three harness-forge councils (Steve Y. + Boris C., 0.3.0 and 0.4.0) flagged that the plugin bundles three products under one manifest — the *kernel/runtime* (engine + the bounded `/harness-run` loop), the *judge* (the 7-critic structural council + `/harness-council`), and the *evals* — and that a kernel-only user carries the council's 8 always-on agent descriptions (~45% of the ~1.9K-token always-on tax) for a review path most operating sessions never take. The council reviews an **external** `.harness/` by path, so it is genuinely separable (a `harness-council` sibling plugin). **Deferred, not declined:** splitting is a real product decision (a second plugin to version, install, and keep in sync) and the maker/runtime/judge do share the rubric vocabulary + the foundations. Interim: the cost is **disclosed** (README "Honest scope" names it; `context-cost.py` measures it). Revisit when the council grows further, or when a real user wants the kernel without the judge. Parallels the brand-forge sub-council pattern (kept bundled because the sub-councils share the *same* job) vs. the plugins-factory pattern (separate from what it judges) — harness-forge sits between, and the call is "bundled until a user needs it apart."

### D-10 · 2026-06-11 — The forked council-calibration checkers stay forked (dedup declined)

The 2026-06-11 real-repo audit (`agent-ops/reviews/2026-06-11-claude-plugins-audit.md`) P0-3/P2-2 flagged the ~10 `evals/council-calibration/check*.py` checkers as ~70% structurally identical and proposed collapsing them into one parameterized `score_transcript(PLANTED, text)`. **The high-value half (rebalance ROI — freeze further calibration-depth, redirect to the missing coverage) was done** (the P0-1 repo-review fixture). The **mechanical dedup is consciously declined**: the 10 checkers live in 4 plugins, so the cleanest single shared core is **forbidden by the zero-cross-plugin-dependency rule**; a per-plugin core saves ~100 net lines but adds `_checklib.py` files + sys.path coupling in `check-recall.py`, for a P2-ranked gain. The duplication is **benign**: the shared part (the `main` + match loop) is ~25 stable lines that rarely change; the volatile part (the `PLANTED` patterns) is already per-checker and **recall-gated** (`check-recall.py`), which can't drift dangerously. Per the audit's own Mechanization-ROI lens, forcing this dedup would be the over-investment it warned against. Revisit only if the boilerplate starts changing often.

### D-9 · 2026-06-11 — The two `check-sourcing.py` are intentionally independent, not drift

The audit's P1-1 flagged `product-forge/bin/check-sourcing.py` (246 lines) vs `agent-ops/bin/check-sourcing.py` (98) as a silent-drift risk — judging by name + line-count. On inspection they are **correctly and intentionally different gates for different provenance surfaces**, and (per the self-contained rule) they *cannot* share code. product-forge gates a dated **research library** (per-reference `date`/`coverage`/`primary_sources` frontmatter) **plus** a council whose obscured critics may defer provenance to the git-ignored name-map — which needs the FULL/PUBLIC-CHECKOUT split (the D-4/R-1 fix). agent-ops has **no research library**, and its obscured critics each carry an **inline `.name-map.md` pointer** (a source signal present in every checkout), so it needs neither the library check nor the public-checkout mode — a simpler design that sidesteps R-1 rather than patching it (green CI on clean clones proves it). Both docstrings now state the relationship (agent-ops already did; product-forge's reciprocal note added). No unification — the divergence is by design.

### D-1 · 2026-06-08 — Marketplace name stays `plugins-forge`; repo is `claude-plugins` · ~~SUPERSEDED by D-12~~

Renaming the marketplace name is breaking: install ids (`brand-forge@plugins-forge`), `~/.claude.json` install state, and sibling repos that enable `@plugins-forge`. The split (repo ≠ marketplace name) is a permanent papercut accepted deliberately. Revisit only under a forced migration. **(2026-06-13: the owner exercised that forced migration — see D-12. The reasoning here stands as the record of why the cost was real, not that the rename was avoided.)**

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

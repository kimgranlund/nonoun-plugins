# Case study — v0.6.37 + v0.6.40 (2026-05-25 / 2026-05-26)

## Catalog-drift recurring — §Step 3.0 graduation was incomplete; v1.9.0 closes the output-staging gap

**Variant:** Mode 1 (Cut & ship) — both occurrences. Same class of CI failure (catalog drift on `verify:components`), same recovery shape (regen + commit follow-up + force-move 10 tags + re-dispatch).

**Status:** Both cycles published 9/9 net of recovery. v0.6.37 took ~5 min of recovery; v0.6.40 took ~5 min of recovery on the **same** class. v1.9.0 graduates the gap that v1.8.0 missed.

---

## What happened — twice

### First occurrence — v0.6.37 (2026-05-25)

7/9 publish workflows failed at the `verify:components` step. The diagnostic was:

```text
[verify] DRIFT catalog: packages/a2ui/corpus/catalog-a2ui_0_9.json
[verify] DRIFT rules: packages/a2ui/corpus/catalog-a2ui_0_9_rules.txt
[verify] 2 file(s) would change. Run build-components.mjs to update.
##[error]Process completed with exit code 1.
```

Root cause: catalog files were modified in WT by peer (uncommitted local audit-token-pair or yaml-sweep work). The release agent correctly excluded the WT pre-state from the release-commit allowlist per multi-agent baseline discipline. **§Step 3.0 didn't run a catalog regen** — the v1.7.0 graduation covered `harvest:chunks` + `build:embeddings:chunks` but not `node scripts/build/components.mjs` (catalog regen).

Recovery: regen + commit follow-up + force-move 10 tags + re-dispatch.

### v1.8.0 graduation — incomplete

The v0.6.37 case study lesson graduated into **adia-ui-release v1.8.0**, which added `node scripts/build/components.mjs` (catalog regen) to §Step 3.0 alongside `harvest:chunks` + `build:embeddings:chunks` + `build:bundles`.

**The graduation covered REGEN but not OUTPUT-STAGING.** Step 3.0 told the agent to regenerate the catalog. It didn't tell the agent that the regen output had to LAND in the release commit even when the same file paths were also peer-in-flight in the working tree.

### Second occurrence — v0.6.40 (2026-05-26)

8/9 publish workflows failed at `verify:components` — only `llm` succeeded (pure ride-along, no catalog dependency). Same diagnostic; same root cause shape.

The release agent followed v1.8.0 §Step 3.0 to the letter — ran `node scripts/build/components.mjs`, got fresh catalog output, ran the gates locally (`verify:components` clean). Then inspected WT:

```text
 M packages/a2ui/corpus/catalog-a2ui_0_9.json       ← peer-in-flight + my regen overlay
 M packages/a2ui/corpus/catalog-a2ui_0_9_rules.txt  ← same
 M packages/web-components/components/badge/badge.d.ts      ← peer-in-flight (NOT mine)
 M packages/web-components/components/card/card.css         ← peer-in-flight (NOT mine)
 M packages/web-components/components/progress-row/progress-row.css  ← peer-in-flight
```

Multi-agent baseline discipline says "stage explicit allowlist; never `git add -A`." Catalog files were on the WT pre-state list as peer-in-flight, so the agent excluded them. **The regen output (correct for this release) also got excluded — same file paths.**

Tags pushed. CI hit DRIFT. 8/9 failed.

Recovery: identical to v0.6.37 — regen + commit follow-up + force-move 10 tags + re-dispatch. ~5 min.

**Twice in the same class is a missing trip-wire.**

---

## What I caught (post-mortem clarity)

The v1.8.0 wording said _regenerate the catalog_. It didn't say:

- "The regen output supersedes any peer-in-flight WT pre-state on the same paths."
- "Catalog files are non-negotiable in the release-commit allowlist when source content changed in the window."
- "Re-verify with `verify:components` after staging — if DRIFT, you excluded the regen output."

All three would have caught the v0.6.40 occurrence. The conflict between "exclude peer WT pre-state" (baseline discipline) and "stage regen output" (§Step 3.0) had no documented winner. The agent resolved the conflict toward exclusion both times.

---

## v1.9.0 graduation — three layers, defense in depth

### Layer 1 — Stronger §Step 3.0 wording (supersedes-WT contract)

The regen step has FOUR deliverables (was implicit; now enumerated):

```bash
node scripts/build/components.mjs           # → catalog + sidecar
npm run harvest:chunks                       # → chunks/_index + per-chunk JSON
npm run build:embeddings:chunks              # → chunk-embeddings.json
npm run build:bundles                        # → dist/*.min.{css,js}
```

**The regen output supersedes any peer-in-flight WT pre-state on the same file paths.** Peer's uncommitted catalog modifications are superseded by the fresh regen — stage the regenerated catalog into the release-commit allowlist UNCONDITIONALLY. Peer can rebase any divergent work on top of the release commit after the cycle.

### Layer 2 — NEW §Step 5.5 — pre-commit verification trip-wire

After `git add` (Step 5) but BEFORE `git commit`, re-run the verify gates one final time:

```bash
node scripts/build/components.mjs --verify    # catalog drift?
npm run check:chunks-fresh
npm run check:embeddings-fresh
```

**Any DRIFT here means a regen output was excluded from staging.** Recovery is in-cycle (no force-push): `git add <drift-paths>` → re-run `verify` until clean → Step 6 (commit).

The trip-wire runs in <2 seconds locally vs ~5 minutes to recover from a CI failure. Pure win.

### Layer 3 — §Step 5 allowlist convention update

When source content changed in this window (yaml / examples.html / contents.html with `data-chunk-*` / status:stable sweeps / Wave commits / OD-5 sweeps), the release-commit allowlist MUST include these regen-deterministic outputs UNCONDITIONALLY:

- `packages/a2ui/corpus/catalog-a2ui_0_9.json`
- `packages/a2ui/corpus/catalog-a2ui_0_9_rules.txt`
- `packages/a2ui/corpus/chunk-embeddings.json`
- `packages/a2ui/corpus/chunks/` (if chunk content drifted)
- `packages/web-components/dist/web-components.min.{css,js}`
- `packages/web-components/dist/icons-manifest.js`
- `packages/web-modules/dist/everything.min.js`
- `packages/web-modules/dist/shell/admin-shell.min.js`
- `packages/web-modules/dist/icons-manifest.js`

These are regen-deterministic outputs; their WT pre-state (if any) is always superseded by the release-cycle regen.

This is **not** "stage WT changes" (still violates multi-agent baseline). This is "stage the regen outputs you produced in §Step 3.0 — they supersede any peer WT pre-state on the same paths."

---

## How v1.9.0 closes the gap (verification target for the next cycle)

For the next v0.6.41+ cycle:

1. Verify peer-in-flight catalog modifications exist in WT (simulate by `touch packages/a2ui/corpus/catalog-a2ui_0_9.json` if needed).
2. Run §Step 3.0 (catalog regen).
3. Stage allowlist per the new convention — catalog UNCONDITIONALLY included.
4. Run §Step 5.5 trip-wire (`node scripts/build/components.mjs --verify` + `check:chunks-fresh` + `check:embeddings-fresh`).
5. Expected: clean. Commit lands; CI passes 9/9 on first dispatch.

If the trip-wire fails: the v1.9.0 graduation is still incomplete; back to the bench.

---

## Cross-references

- Sibling case studies:
  - [freshness-gate-recovery-v0.6.32](./2026-05-23-freshness-gate-recovery-v0.6.32.md) — same pattern shape: CI failure detected at publish time → graduation into §Step 3.0 (this case is the v1.8.0 → v1.9.0 iteration). v0.6.32 → v1.7.0 graduated cleanly; v0.6.37 → v1.8.0 graduated incompletely.
  - [corpus-drift-remediation-v0.6.15](./2026-05-20-corpus-drift-remediation-v0.6.15.md) — earlier embeddings drift (6.6 days stale, batch-push context).
- Audit-history ledgers:
  - `.brain/audit-history/2026-05-25-release-cut-v0.6.37.json`
  - `.brain/audit-history/2026-05-26-release-cut-v0.6.40.json`
- FEEDBACK ticket that motivated this graduation: `FEEDBACK-75` (the internal release-cycle self-feedback ticket)

## Lesson aphorism

> "Once is happenstance, twice is coincidence, twice in the same class is a missing trip-wire."

The release skill survives because every CI failure that recurs gets graduated into mechanical defense, not into a longer recovery runbook.

# Case study — v0.6.32 (2026-05-23)

## Freshness-gate recovery: deploy-handoff variant catching pre-flight gap

**Variant:** Mode 3 (Deploy peer handoff) + freshness-gate recovery preamble.

**Status:** Resolved cleanly. 9/9 npm publishes succeeded on first dispatch. Tags re-pointed without force-push.

---

## What happened

Peer (Kim) pre-authored v0.6.32 release commit `5285defa8` after a substantive substrate sweep:

- `60a247efa` — tag/badge/segment phantom-gap fix
- `6db1d8a58` — FB-51 P0: `everything.min.js` now registers all 95+ primitives (was incomplete)
- `e394a8099` — remove duplicate `data-chunk-kind` attrs
- `d8f4ff2c0` — admin-shell `[data-col]/[data-row]` CSS scoped to ancestor
- **`5d8c62a80`** — feat(0.6.32): everything.js bundle fix + icons-manifest + llms.txt + **status:stable sweep on all 141 component YAMLs + anatomy sweep across examples pages**
- `5285defa8` — release commit + 10 tags created locally

The status:stable yaml sweep + anatomy sweep touched 284 yaml/json files. The chunk corpus is yaml-derived — peer's sweep regenerated the yaml sources but **did not run `harvest:chunks` + `build:embeddings:chunks`** as a follow-on step.

Peer's commit message claimed verification was green with 7 gates enumerated:

> check:lockstep OK / verify:components clean / verify:traits 56/56 / check:css-bundles-fresh 5/5 / check:js-bundles-fresh 6/6 / smoke:engines ok / test:a2ui 22/22

**The remaining 9 of 16 gates were skipped** — including `verify:corpus`, `check:chunks-fresh`, `check:embeddings-fresh`, and `check:links`. The post-yaml drift was invisible to peer's automation.

## What I caught

User instruction: _"re-harvest the chunks then cut 0.6.32"_

Operator probe acting as forensic gate. I picked up the cycle at deploy-handoff state (release commit + tags pre-created locally, tags not yet pushed), ran `npm run harvest:chunks`:

- 387 chunk instances parsed → 238 unique → 190 leaf + 48 nested-expanded
- **230+ chunk JSON files updated** + `chunks/_index.json` regenerated

Then `check:embeddings-fresh` reported:

```text
[embeddings] FAILED — drift detected:
  ✗ chunk-embeddings.json is 1.0d older than chunks/_index.json
    — run `npm run build:embeddings:chunks`
```

## Recovery (clean — no force-push)

Because peer's tags were local-only (never pushed to origin), recovery was a tag-move, not a tag-rewrite:

1. `npm run build:embeddings:chunks` — regenerated chunk-embeddings.json (OpenAI text-embedding-3-small, 8 batches, 238 × 1536d, ~6.8 MB)
2. Updated `@adia-ai/a2ui-corpus [0.6.32]` CHANGELOG entry to document the regen (replaced peer's `_No pending changes._` placeholder).
3. Committed `chunks/` + `chunk-embeddings.json` + CHANGELOG as `e864fc396 chore(a2ui-corpus): v0.6.32 re-harvest — 238 chunks + embeddings regen`.
4. Re-ran the FULL 16-gate Step 3 roster. All green (`verify:corpus` exit code 0; 65 pre-existing warnings carried forward — 61 field-wraps-widget + 4 enum-out-of-range, all technical debt unrelated to v0.6.32).
5. Deleted local tags at `5285defa8`, recreated all 10 at `e864fc396`:

   ```bash
   for tag in v0.6.32 web-{components,modules}-v0.6.32 llm-v0.6.32 \
              a2ui-{compose,corpus,mcp,retrieval,runtime,validator}-v0.6.32; do
     git tag -d $tag && git tag $tag HEAD
   done
   ```

6. F-N1 (`check:release --all-pending`): 9/9 per-package clean.
7. Pushed branch + 10 tags, dispatched 9 publish workflows → 9/9 success on first dispatch.

## Key lessons graduated into the skill

### 1. Step 3 grew §Step 3.0 (harvest preamble)

When source content changes (yaml / examples / contents.html with data-chunk-\* annotations / status:stable sweeps / anatomy sweeps), proactively run `harvest:chunks` + `build:embeddings:chunks` BEFORE the gates — not reactively after they fail. Cheap to run, catches drift before it lands in a tag.

Documented in `cycle-happy-path.md` §Step 3.0 with source-content signal list + recipe.

### 2. Step 3 grew an explicit "all 16 must run" rule

The previous Step 3 listed the gates but didn't forbid selective subsets. Peer's automation enumerated 7. The rule is now:

> **All 16 gates MUST run. Selective subset = pre-flight failure.**

Documented in `cycle-happy-path.md` §Step 3.1 with the canonical roster numbered 1-16.

### 3. The recovery recipe is preserved as this case study

Future cycles facing the same situation can follow this playbook:

- Tags local-only → safe to delete + recreate at new HEAD
- Tags pushed → either force-push tags (rare, document why) or roll forward to next version
- Always: re-run F-N1 after tag-move; full 16-gate roster after harvest preamble.

## Cross-references

- Audit-history ledger: `.brain/audit-history/2026-05-23-release-cut-v0.6.32.json`
- Release notes draft: `/tmp/release-v0.6.32/notes.md`
- Sibling case studies:
  - [corpus-drift-remediation-v0.6.15](./2026-05-20-corpus-drift-remediation-v0.6.15.md) — earlier embeddings drift (6.6 days stale, batch-push context).
  - [version-skip-correction-v0.6.12](./2026-05-20-version-skip-correction-v0.6.12.md) — adjacent recovery pattern (tag-rewrite, force-push variant).

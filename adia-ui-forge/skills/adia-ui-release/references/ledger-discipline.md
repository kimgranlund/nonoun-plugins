# `ledger-discipline.md` — audit-history JSON schema + what to capture

> Loaded by mode 1 Step 11 (Ledger), mode 4 (batch-push ledger), and mode 8 (Investigation — reads past ledgers).

Every release cycle writes a JSON ledger to `.brain/audit-history/YYYY-MM-DD-<kind>-vX.Y.Z.json`. The ledger is the long-term memory of the cycle — what shipped, what was excluded, what was learned. Future cycles read past ledgers (mode 8) and the post-mortem flow (mode 7 + `ops-postmortem` skill) cross-references them.

This file documents the canonical schema + what to capture for each release-kind.

---

## §The canonical schema

```json
{
  "kind": "release-cut" | "batch-push" | "p1-hotfix" | "post-release-fix",
  "audit_id": "YYYY-MM-DD-<kind>-vX.Y.Z",
  "repo": "<org>/<repo>",
  "released_at": "YYYY-MM-DD",
  "version": "X.Y.Z",
  "release_type": "MAJOR" | "MINOR" | "PATCH",
  "summary": "<one-paragraph>",
  "scope": { /* free-form keys, one per substantive package or topic */ },
  "release_commit": "<sha>",
  "tag_commit": "<sha>",
  "tags": [ /* all 10 tags */ ],
  "verification": { /* gate-by-gate summary */ },
  "publish_workflows": { "dispatched": "9/9 ...", "conclusions": "9/9 success" },
  "notes": [ /* one entry per lesson, exclusion, anomaly */ ]
}
```

The `audit_id` is the file's basename (without `.json`). The `.brain/audit-history/` directory accumulates one such ledger per release cycle. (`make-ledger.mjs` scaffolds the file from git state + `--repo-slug`; the `9/9` counts below are the @adia-ai monorepo's 9-package worked example — substitute your monorepo's package count.)

No `$schema` key: ledgers are self-describing local audit records, so `make-ledger.mjs` deliberately emits no `$schema` (it pointed at a non-bundled external host that this skill does not own or validate against). If your ops setup validates ledgers against a hosted JSON Schema, add the `$schema` field in your own post-processing.

---

## §What every ledger MUST capture

These fields are required and the cycle is incomplete without them:

### `audit_id` + `released_at` + `version`

- `audit_id` matches the filename. Format: `YYYY-MM-DD-release-vX.Y.Z` (single-version) or `YYYY-MM-DD-batch-push-vA-vZ` (batch).
- `released_at` is the YYYY-MM-DD cycle date.
- `version` is the published semver (no `v` prefix).

### `summary` (the one-paragraph)

A single paragraph (4–6 sentences) covering: substantive packages + scope + new primitives/APIs + retracted features + bundled skill cuts. This is what future operators READ when grepping `.brain/audit-history/`.

Example (v0.6.21):

> "9-package lockstep PATCH cut, authored from scratch. @adia-ai/web- components: table-ui truncate-by-default with [wrap]/[data-wrap] opt-in (§403), toast/feed-item variant text colour fix, input-ui slot-label spacing. @adia-ai/web-modules: `<admin-entity-item>` row- inset alignment, FEEDBACK-37 retraction (admin-shell spurious slot- contract console.warn removed), page-header title-row :first-of-type selector fix. @adia-ai/a2ui-corpus: catalog regen."

### `release_commit` + `tag_commit`

- `release_commit`: the SHA of the actual `chore(release):` or `release(*):` commit (typically the same as `tag_commit` unless an enrichment-pass amended it).
- `tag_commit`: the SHA the 10 tags point at (= HEAD at tag time).

If those differ (F-N1 enrichment scenario), record BOTH and explain in a `notes` entry.

### `tags` array

All 10 tags (umbrella + 9 per-package), in that order.

### `verification` (gate-by-gate)

A flat object with gate-name → status. Use the same keys across cycles so future search can find regression patterns:

```json
"verification": {
  "check_lockstep": "OK at X.Y.Z / ^X.Y.0",
  "test_unit": "NNNN/NNNN across NN files",
  "typecheck": "clean",
  "components_verify": "clean — NN files",
  "verify_traits": "56/56 (100%)",
  "check_demo_shells": "clean — NN shells",
  "check_lightningcss_build": "NN CSS files clean",
  "verify_corpus": "0 errors / 0 warns",
  "check_embeddings_fresh": "OK",
  "check_links": "NNNN files clean",
  "smoke_engines": "green",
  "smoke_register_engine": "11/11",
  "eval_diff_zettel": "cov=N% avg=N (floor cov≥5% avg≥85)",
  "fn1_trip_wire": "9/9 per-package clean ...",
  "npm_latest": "X.Y.Z across all 9 packages",
  "exe_serves": "HTTP 200 (gen-ui)",
  "gh_releases": "9 created per-package"
}
```

Use underscores (`check_demo_shells`) not colons (`check:demo-shells`) in JSON keys — colons aren't valid JSON identifier punctuation.

If a gate FAILED at first and was recovered — record the recovery in `notes`, not in `verification` (which shows final state).

### `publish_workflows`

```json
"publish_workflows": {
  "dispatched": "9/9 via gh workflow run --ref <pkg>-vX.Y.Z",
  "conclusions": "9/9 success"
}
```

For batch push, expand:

```json
"publish_workflows": {
  "dispatched": "18/18 — vA.B.C set dispatched + settled FIRST, then vA.B.D set (ordering ensures npm latest lands on vA.B.D)",
  "conclusions": "18/18 success"
}
```

### `notes` (the lesson log)

Array of strings, one per significant observation. Examples:

- "STALE TEST FIXED: ..." — when a stale test required updating.
- "PEER-IN-FLIGHT EXCLUDED: ..." — when a peer file was stashed.
- "STRAY UNCOMMITTED CHANGE EXCLUDED: ..." — when an uncommitted-but-undocumented change was stashed.
- "F-N1 flagged N cosmetic diff-coverage warns; enrichment pass applied to ..." — when the enrichment pass ran.
- "Companion: `<companion-plugin>` vX.Y.Z bundled with this cut" — when a tooling/skill update rides along.
- "Umbrella tag vX.Y.Z fails F-N1 pattern check — expected; lockstep convention" — boilerplate but worth keeping for archaeological consistency.

The `notes` array is the **highest-information part of the ledger**. This is what future operators read first when investigating a past release.

---

## §What ELSE to capture per kind

### `kind: release-cut` (standard single-version)

Add `scope` keys per substantive package:

```json
"scope": {
  "web_components": "<one-sentence per substantive feature in this package, with FEEDBACK numbers>",
  "web_modules": "<same>",
  "a2ui_corpus": "<same>",
  "ride_along_stubs": "@adia-ai/llm, @adia-ai/a2ui-compose, ... — version bump only."
}
```

### `kind: batch-push` (multi-version)

Add `versions` array + per-version `tag_commits` + `scope` per-version:

```json
"versions": ["A.B.C", "A.B.D"],
"tag_commits": {
  "vA.B.C": "<sha>",
  "vA.B.D": "<sha>"
},
"scope": {
  "vA.B.C": "<one-paragraph summary of this version>",
  "vA.B.D": "<same>"
}
```

### `kind: p1-hotfix` (urgent fix without normal cycle)

Add `incident` block:

```json
"incident": {
  "trigger": "<the symptom that demanded a hotfix>",
  "detection_lag": "<when shipped → when noticed>",
  "scope_minimization": "<what was deliberately NOT included to keep the hotfix small>"
}
```

Cross-reference `ops-postmortem` skill — the hotfix usually pairs with a postmortem doc.

### `kind: post-release-fix` (correction after publish)

Add `corrects` block:

```json
"corrects": {
  "version": "<the version being corrected>",
  "issue": "<what was wrong>",
  "resolution_path": "<how — typically a follow-up release>"
}
```

Example: a future "v0.6.21.1" or "v0.6.22 fix-only" cycle correcting a v0.6.21 defect would carry this block.

---

## §Where to write it

Path: `.brain/audit-history/YYYY-MM-DD-release-vX.Y.Z.json`.

Convention:

- Date is the cycle's `released_at` field (not strictly the local filesystem date; they should match but the field is authoritative).
- For batch push: `.brain/audit-history/YYYY-MM-DD-batch-push-vA-vZ.json` where A is the oldest and Z is the newest version in the batch.

The file MUST be added in a separate `chore(audit-history)` commit after the release commit ships. Don't bundle it into the release commit — the ledger commit is the cycle's epilogue.

---

## §Reading past ledgers (mode 8)

When the operator asks "what shipped in v0.6.X?" or "did we ever fix `<symptom>`?":

```bash
# Single-version lookup
cat .brain/audit-history/*-release-v0.6.X.json | jq .

# Search across cycles
grep -l "FEEDBACK-37" .brain/audit-history/*.json | sort
grep -l "stale test" .brain/audit-history/*.json | sort
grep -l "version-skip" .brain/audit-history/*.json | sort

# What gates were ever flagged?
for f in .brain/audit-history/*.json; do
  echo "$(basename $f):"
  jq -r '.notes[] | select(test("FAILED|enrichment|STASHED|EXCLUDED"))' "$f" 2>/dev/null
done
```

Memory: `reference_findings_index_and_postmortems` — there's a `.brain/findings/INDEX.md` for open follow-ups and `.brain/postmortems/` for incident write-ups. The audit-history ledgers complement those: ledgers are per-cycle, INDEX/postmortems are per-issue.

---

## §When this reference is "done v1"

- Every cycle's ledger uses the canonical schema with no key drift (verifiable via a JSON schema validator or `jq` keys diff).
- The `notes` array has at least one entry per cycle (the umbrella F-N1 boilerplate counts as the minimum).
- The next mode-8 investigation (what shipped in v0.6.X?) reads the ledger first, not the GH release page.

# Case study — v0.6.14 + v0.6.15 batch push

**Cycle:** 2026-05-20 (v0.6.13 → v0.6.14 + v0.6.15) **Scenario:** `recovery-paths.md` § Scenario 2 (batch push) **Source ledger:** `.brain/audit-history/2026-05-20-batch-push-v0.6.14-v0.6.15.json` **Outcome:** 2 unpushed accumulated releases shipped together, npm `latest` correctly landed on the newer version.

---

## §The shape

User asked: _"prepare and initiate 0.6.15 release"_.

Operator re-baselined and found:

- 12 unpushed commits since the last published v0.6.13 ledger.
- **TWO** release commits in the unpushed range:
  - `fe30897a7 release(*): v0.6.14 lockstep — <admin-page-header> distinct background + drop-shadow`
  - `4793fc683 release(*): v0.6.15 lockstep — icon-loader DX repair (FB-07/08/09) + dashboard chunk vertical-rhythm self-styling`
- NO tags for either version.
- npm latest: `0.6.13`.

A peer agent had cut both releases locally but didn't push or publish. The user asked specifically for v0.6.15 — but v0.6.14 was a real intermediate release with its own CHANGELOG. Skipping it on npm would leave a permanent gap in version history.

---

## §The diagnosis

Two release commits + intermediate substantive work between them = **batch push** (mode 4 in `adia-ui-release`).

Validating "yes both are real releases" (vs "v0.6.14 is a draft to squash"):

- Each release commit has its own per-package `## [vX.Y.Z]` block in the 9 CHANGELOGs.
- Each release commit bumped versions cleanly (v0.6.13 → v0.6.14 in `fe30897a7`; v0.6.14 → v0.6.15 in `4793fc683`).
- The substantive content between them is independent: v0.6.14 is a visual treatment for page-header bg + drop-shadow; v0.6.15 is icon- loader DX repair (FB-07/08/09) + corpus chunk re-harvest.

Both ship as-is.

---

## §The fix

The batch push protocol:

### 1. Tag each version at its OWN release-commit SHA

Not at HEAD — at the commit where each version was actually cut. This is the EXCEPTION to the standard "tag at HEAD" invariant (`SKILL.md` § ReleaseInvariants #3). Memory: `feedback_tag_at_head_not_bump_commit`.

```bash
git tag v0.6.14 fe30897a7
git tag v0.6.15 4793fc683
# + 9 per-package tags for each → 20 tags total
```

### 2. F-N1 against ALL pending tags

```bash
node scripts/release/check-release.mjs --all-pending
```

Expected: 9/9 per-package clean for each version (umbrella errors expected; "HEAD-ahead" warns on v0.6.14 per-package tags are expected — v0.6.15 content legitimately landed after the v0.6.14 tag).

### 3. Push main (sweeps all commits) + 20 tags

```bash
git push origin main
git push origin v0.6.14 v0.6.15 \
  web-components-v0.6.14 web-components-v0.6.15 \
  web-modules-v0.6.14 web-modules-v0.6.15 \
  ... # (18 per-package tags + 2 umbrella)
```

### 4. Publish IN ORDER — v0.6.14 FIRST, then v0.6.15

**Critical**: `npm dist-tag latest` is set by publish order. Dispatch v0.6.14's 9 workflows, WAIT for completion, verify all 9 success, THEN dispatch v0.6.15's 9 workflows.

```bash
# Dispatch v0.6.14 set
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  gh workflow run "publish-$pkg.yml" --ref "$pkg-v0.6.14"
done

# Wait for v0.6.14 to settle
until [ "$(gh run list --workflow=publish-a2ui-validator.yml \
  --limit 1 --json status -q '.[0].status')" = "completed" ]; do
  sleep 5
done

# Verify all 9 v0.6.14 publishes succeeded — check conclusion is "success"
# Then dispatch v0.6.15 set
for pkg in web-components web-modules ...; do
  gh workflow run "publish-$pkg.yml" --ref "$pkg-v0.6.15"
done
```

The CLI helper `scripts/dispatch-publish.mjs --version 0.6.15 --after 0.6.14` automates the npm-latest-verification gate.

### 5. Discovery during publish — embeddings drift

While running pre-flight against the v0.6.15 commit, the operator caught `check:embeddings-fresh` failing:

```text
[embeddings] FAILED — drift detected:
  ✗ chunk-embeddings: packages/a2ui/corpus/chunk-embeddings.json is 6.6d older than chunks/_index.json
```

The v0.6.15 commit re-harvested 10 dashboard corpus chunks but didn't regenerate the embedding index. The operator ran `npm run build:embeddings:chunks` (230 chunks re-embedded in ~6 seconds), staged `chunk-embeddings.json`, and **enriched the a2ui-corpus [0.6.15] CHANGELOG entry** to note the regen.

Then committed (`6ef083953`) and re-tagged v0.6.15 at the new HEAD — the embeddings commit is part of the v0.6.15 release window.

### 6. Single batch-push ledger

Instead of two per-version ledgers, write ONE `2026-05-20-batch-push-v0.6.14-v0.6.15.json` covering both versions:

```json
"kind": "batch-push",
"versions": ["0.6.14", "0.6.15"],
"tag_commits": {
  "v0.6.14": "fe30897a7",
  "v0.6.15": "6ef083953"
},
"publish_workflows": {
  "dispatched": "18/18 — v0.6.14 set dispatched + settled FIRST, then v0.6.15 set (ordering ensures npm latest lands on 0.6.15)",
  "conclusions": "18/18 success"
}
```

---

## §The lesson

1. **Multiple unpushed release commits = batch push.** Don't skip a version; don't squash unrelated work.
2. **Tag each version at its own release-commit SHA.** Exception to the standard tag-at-HEAD rule.
3. **Publish in version order.** npm `latest` is publish-order-set. The `--after` flag in `dispatch-publish.mjs` enforces this by verifying npm latest before dispatching.
4. **Pre-flight at the LATER tag's SHA still gates the cycle.** The embeddings-drift catch is a Phase 1 gate (`check:embeddings-fresh`); failure routes to corpus remediation (here, `npm run build:embeddings:chunks` — staged into the v0.6.15 release window via a new commit `6ef083953`).
5. **One ledger per batch, not per version.** The `kind: batch-push` schema variant in `ledger-discipline.md` handles the multi-version shape.

---

## §Cross-references

- `../../references/recovery-paths.md` § Scenario 2 — the protocol checklist
- `../../references/gates-catalog.md` § Category 7 § `check:embeddings-fresh` — the gate that caught the drift
- `../../references/ledger-discipline.md` § What ELSE to capture per kind § `kind: batch-push`
- Repo precedent: `2026-05-19-batch-push-v0.6.1-v0.6.6.json` — the 6-release batch push that established the per-version tag SHA protocol.
- Repo memory: `feedback_tag_at_head_not_bump_commit` documents the invariant + its exception.

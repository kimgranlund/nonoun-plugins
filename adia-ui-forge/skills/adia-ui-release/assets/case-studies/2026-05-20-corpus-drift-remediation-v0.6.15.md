# Case study — corpus drift remediation (v0.6.15)

**Cycle:** 2026-05-20 (v0.6.14 + v0.6.15 batch push) **Scenario:** `gates-catalog.md` § Category 7 § `check:embeddings-fresh` failure **Source ledger:** `.brain/audit-history/2026-05-20-batch-push-v0.6.14-v0.6.15.json` **Outcome:** `chunk-embeddings.json` 6.6d stale; regenerated 230 chunks; staged into the v0.6.15 release window via a new commit; cycle proceeded clean.

---

## §The shape

Pre-flight pass against the v0.6.15 commit-candidate failed at `check:embeddings-fresh`:

```text
[embeddings] FAILED — drift detected:
  ✗ chunk-embeddings: packages/a2ui/corpus/chunk-embeddings.json
    is 6.6d older than chunks/_index.json — run `npm run build:embeddings:chunks`
```

The v0.6.15 commit re-harvested 10 dashboard corpus chunks (`§403 table-ui + admin-dashboard.contents.html` → re-emitted as `<col-ui gap=4>` for self-styling). The chunks/\_index.json updated to reference them. But `chunk-embeddings.json` (the retrieval embedding index built FROM the chunks) was not regenerated — it remained at the v0.6.10-ish mtime.

---

## §The diagnosis

**Embeddings stale relative to chunks** = retrieval mismatches. `smoke:engines` retrieval probes were still passing (the corpus overlap was enough for the smoke probes to match), but a real cycle needs the embedding index in sync with the chunk content. A substantive corpus refresh that doesn't re-embed is incomplete.

Routing per `gates-catalog.md` § `check:embeddings-fresh`:

> **Recovery:** `npm run build:embeddings:chunks`. Requires `OPENAI_API_KEY` env. ~6 seconds for ~230 chunks at `text-embedding-3-small`. Stage `chunk-embeddings.json`; add a note to the a2ui-corpus CHANGELOG `[vX.Y.Z]` entry.

The remediation is in-house (the script exists; the operator just needs to run it). Not a route-to-`adia-ui-a2ui` case (corpus drift remediation in `adia-ui-a2ui` is for harvest-time / catalog- regen failures — this is the simpler "embedding index is stale" case).

---

## §The fix

### 1. Regenerate the embedding index

```bash
npm run build:embeddings:chunks
```

Output:

```text
[embeddings-chunks] 230 chunk(s) to embed
[embeddings-chunks] provider: openai (text-embedding-3-small)
  batch 1 (1–32) … 1850ms
  batch 2 (33–64) … 655ms
  ...
  batch 8 (225–230) … 176ms
[embeddings-chunks] wrote 230 × 1536d → chunk-embeddings.json (6632 KB)
```

Total wall time: ~6 seconds. Required `OPENAI_API_KEY` env (operator had it set; if not — coordinate with operator to provide).

### 2. Verify

```bash
npm run check:embeddings-fresh
# [embeddings] OK — both indexes at-or-newer-than their source
#   chunk-embeddings: 2026-05-21T04:57:40.966Z
```

Clean.

### 3. Stage into the v0.6.15 release window via a NEW commit

The v0.6.15 release commit was already cut at `4793fc683`. The embeddings regen is a fix-up of v0.6.15's OWN corpus change — it belongs in the v0.6.15 window. New commit on top:

```bash
git reset HEAD >/dev/null 2>&1
git add packages/a2ui/corpus/chunk-embeddings.json \
        packages/a2ui/corpus/CHANGELOG.md  # also enrich the [0.6.15] entry

git commit -m "$(cat <<'EOF'
chore(corpus): regenerate chunk-embeddings.json for v0.6.15 chunk re-harvest

The v0.6.15 release commit (4793fc683) re-harvested 10 dashboard corpus
chunks but did not regenerate the retrieval embedding index.
check:embeddings-fresh failed — chunk-embeddings.json had drifted 6.6
days stale relative to chunks/_index.json.

Regenerated all 230 chunk embeddings (1536-d text-embedding-3-small).
check:embeddings-fresh now green. a2ui-corpus [0.6.15] CHANGELOG entry
notes the regen.

Part of the v0.6.15 release window — v0.6.15 tags land at this commit.
EOF
)"
```

### 4. Enrich the a2ui-corpus CHANGELOG `[0.6.15]` entry

Added a `### Changed` bullet describing the regen:

```markdown
- **`chunk-embeddings.json` regenerated to match the re-harvested chunks.**
  230 chunks re-embedded (1536-d `text-embedding-3-small`); restores
  `check:embeddings-fresh` to green — the retrieval index had drifted
  6.6 days stale relative to `chunks/_index.json`, predating this cut
  but surfaced by the dashboard chunk re-harvest above.
```

### 5. Re-tag v0.6.15 at the new HEAD

The v0.6.15 tags now point at `6ef083953` (the embeddings regen), NOT `4793fc683` (the original release commit). Per the standard tag-at-HEAD invariant — the release window extends to include the completing fix.

```bash
# Delete old tags
git tag -d v0.6.15 web-components-v0.6.15 ... # all 10
# Re-create at new HEAD
git tag v0.6.15
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  git tag "$pkg-v0.6.15"
done
```

### 6. F-N1 + push + publish

Standard cycle from here. F-N1 9/9 clean (the CHANGELOG enrichment + the embedding-regen commit landed in the same release window).

---

## §The lesson

1. **`check:embeddings-fresh` is a real gate.** Don't skip it just because `smoke:engines` retrieval probes pass — they pass via overlap, not via correctness.
2. **Embedding regen is fast.** ~6 seconds for 230 chunks at `text-embedding-3-small`. No reason to defer.
3. **It belongs in the SAME release window** that re-harvested the chunks. The embedding index is a fix-up of the same source change. Tag at the new HEAD (the embedding-regen commit), NOT at the release commit.
4. **Enrich the CHANGELOG entry** to mention the regen. F-N1 will look for the keyword; the entry needs to describe the `chunk-embeddings.json` change naturally.
5. **OPENAI_API_KEY dependency.** The `build:embeddings:chunks` script calls the OpenAI embeddings API. If the env isn't set, the script fails immediately — coordinate with the operator to provide credentials before running.

---

## §Ledger fragment

```json
"verification": {
  "check_embeddings_fresh": "FAILED at HEAD (6.6d stale) → regenerated 230 chunks (1536-d text-embedding-3-small) → now green"
},
"notes": [
  "check:embeddings-fresh FAILED at HEAD — the v0.6.15 chunk re-harvest updated chunks/_index.json but chunk-embeddings.json was not regenerated (6.6 days stale, predating this cut). Deploy session regenerated it (commit 6ef083953) and added a line to the a2ui-corpus [0.6.15] CHANGELOG. v0.6.15 tags land at 6ef083953 (release window HEAD)."
]
```

`grep -l "embeddings-fresh FAILED" .brain/audit-history/*.json` finds cycles that hit this scenario.

---

## §Cross-references

- `../../references/gates-catalog.md` § Category 7 § `check:embeddings-fresh` — the gate definition + recovery path
- `../../references/cycle-happy-path.md` § Step 3 — pre-flight gate roster
  - the embedding-fresh check
- `../../references/changelog-discipline.md` § Authoring — fresh-block authoring path (used here to ENRICH an existing block; same discipline)
- `adia-ui-a2ui` skill — the broader corpus harvest / drift remediation home (this case study is the simpler "embedding index stale" subset)

# Case study — F-N1 diff-coverage enrichment pass (v0.6.19)

**Cycle:** 2026-05-21 (v0.6.18 → v0.6.19) **Scenario:** `recovery-paths.md` § F-N1 cosmetic warns → enrich path keywords **Source ledger:** `.brain/audit-history/2026-05-21-release-v0.6.19.json` **Outcome:** 2 cosmetic warns converted to 9/9 clean via 2-line CHANGELOG wording tweaks + commit amend + re-tag.

---

## §The shape

Operator authored v0.6.19 from scratch (claims-ui-v4 FB-22…33 batch). After tagging, F-N1 (`check:release --all-pending`) reported 2 warns:

```text
⚠ [warn] diff 'packages/a2ui/corpus/chunks/' touched between
  a2ui-corpus-v0.6.18 → a2ui-corpus-v0.6.19 but CHANGELOG [0.6.19]
  doesn't mention 'chunks'

⚠ [warn] diff 'packages/web-components/core/' touched between
  web-components-v0.6.18 → web-components-v0.6.19 but CHANGELOG [0.6.19]
  doesn't mention 'core'
```

Both changes WERE documented:

- a2ui-corpus entry described "~235 chunk JSON files re-harvested" + "Companion `chunk-reconcile` triage" — but neither literally used the keyword `chunks` (path token).
- web-components entry described "`UIElement.ensure()` part-wipe invariant" — described `UIElement` extensively but didn't say `core` (path token).

F-N1's diff-coverage regex matches **literal path tokens**. The entries were content-complete but missed the regex's keyword.

---

## §The diagnosis

Cosmetic vs real failure decision (per `changelog-discipline.md` § F-N1 enrichment):

> Read the CHANGELOG entry: does any bullet describe the touched files (by component name, by what the change does)? If yes → cosmetic → enrich. If no → real → author.

Both bullets described the touched code — `~235 chunk JSON files` and `UIElement.ensure() part-wipe invariant`. Cosmetic warns.

---

## §The fix

Two minimal wording tweaks to inject the path keywords naturally:

### a2ui-corpus entry

Before:

```text
Freshened the stale chunk corpus: ~235 chunk JSON files re-harvested/reconciled
```

After:

```text
Freshened the stale corpus chunks: ~235 JSON files under `chunks/` re-harvested/reconciled
```

Word reorder ("chunk corpus" → "corpus chunks") + add the path reference `under \`chunks/\``. Both keywords now present; reads naturally; conveys the same information.

### web-components entry (FEEDBACK-31 section)

Before:

```text
- `ensure()` marks stamped structural parts with `_uiPart = true` and its
  doc comment states the invariant: ...
```

After:

```text
- `UIElement.ensure()` (`core/element.js`) marks stamped structural parts
  with `_uiPart = true` and its doc comment states the invariant: ...
```

Add the file path inline as a parenthetical. Now mentions `core/`; also makes the entry more accurate (names the actual file).

### Amend + re-tag + re-run

```bash
git add packages/a2ui/corpus/CHANGELOG.md packages/web-components/CHANGELOG.md
git commit --amend --no-edit

# Delete + re-create 10 tags (SHA moved)
git tag -d v0.6.19 web-components-v0.6.19 web-modules-v0.6.19 ... # all 10
git tag v0.6.19
for pkg in web-components web-modules llm a2ui-runtime a2ui-compose \
           a2ui-corpus a2ui-mcp a2ui-retrieval a2ui-validator; do
  git tag "$pkg-v0.6.19"
done

# Re-run
node scripts/release/check-release.mjs --all-pending
# → 9/9 per-package ✓ clean (umbrella error expected)
```

---

## §The lesson

1. **F-N1 cosmetic warns are common and trivially fixed.** Two wording tweaks resolved both. Total work: ~5 minutes.
2. **Read the warn for the keyword.** The message says exactly what string is missing (`'chunks'`, `'core'`). Add that string to a natural place in the entry.
3. **Don't padding-pad.** Forcing a keyword into the entry as a sidecar parenthetical reads worse than weaving it in. The "components/table/table.yaml" path-reference style is the standard — it conveys file path AND makes the entry more accurate.
4. **Amend, don't add a new commit.** The CHANGELOG enrichment IS part of the release commit conceptually. `git commit --amend --no-edit` keeps the release commit clean. The tag SHA moves; just re-tag.
5. **Bonus — the v0.6.21 cycle adopted this discipline at authoring time.** Peer commit `d8cbbd30c` was explicitly named _"uses full path so F-N1 gate matches"_ — i.e. the peer learned the pattern and started authoring entries with full file paths from the start. By v0.6.21 the F-N1 cycle was 9/9 clean on first pass.

---

## §Ledger fragment

```json
"notes": [
  "F-N1 flagged 2 cosmetic diff-coverage warns on the first tag pass (a2ui-corpus chunks/ + web-components core/ touched but CHANGELOG lacked the literal path keyword). Both fixed by minor wording tweaks; release commit amended; re-tagged at 8d48845ad; F-N1 re-run 9/9 clean."
]
```

`grep -l "diff-coverage" .brain/audit-history/*.json` finds cycles that needed this enrichment pass.

---

## §Cross-references

- `../../references/changelog-discipline.md` § F-N1 diff-coverage enrichment — the canonical procedure
- `../../references/gates-catalog.md` § Category 1 § F-N1 — the gate definition + cosmetic-vs-real failure decision tree
- Repo precedent: peer commit `d8cbbd30c docs(web-components/CHANGELOG): §403 table-ui entry uses full path so F-N1 gate matches` — the peer adopting the discipline at authoring time

# `changelog-discipline.md` — Keep-a-Changelog mechanics + F-N1 enrichment

> Loaded by modes 1, 2 when a CHANGELOG touch is needed (Variant B author-from-scratch always; Variant A only if F-N1 enrichment warns).

The AdiaUI monorepo uses [Keep a Changelog](https://keepachangelog.com/) shape per-package, with the convention that the release-cut cycle **promotes** `## [Unreleased]` content into `## [vX.Y.Z] — YYYY-MM-DD` at cut time. This file documents that mechanic + the F-N1 diff-coverage path-keyword discipline that catches when a CHANGELOG entry describes a change but doesn't use the literal path token the release trip-wire expects.

---

## §The 4 CHANGELOG shapes

Across the 9 packages, every per-cycle CHANGELOG entry falls into one of these shapes:

| # | Shape | When |
| --- | --- | --- |
| 1 | **Substantive — promoted** | Package has `[Unreleased]` content; cut renames the heading |
| 2 | **Substantive — authored** | Package has source change but no `[Unreleased]` block (e.g. corpus regen reflected only by yaml→a2ui regeneration); cut writes a fresh block |
| 3 | **Stub** | Package has no source change at all; cut inserts the lockstep stub |
| 4 | **Cycle-aware enrichment** | Substantive entry exists but doesn't include a path keyword F-N1 wants — add the keyword inline |

The §Promotion mechanic, §Authoring mechanic, and §F-N1 enrichment sections below cover each.

---

## §Promotion — `[Unreleased]` → `[vX.Y.Z] — YYYY-MM-DD`

When a peer has staged work under `## [Unreleased]` and the cycle is cutting that version, the heading swap is **all** that needs to happen. The content under it (`### Added`, `### Fixed`, etc.) becomes the new version block as-is.

**Pattern:**

```text
## [Unreleased]

### Added — <thing>
- <bullets>

## [0.6.X-1] — 2026-05-21
```

becomes

```text
## [0.6.X] — 2026-05-21

### Added — <thing>
- <bullets>

## [0.6.X-1] — 2026-05-21
```

The CLI helper `scripts/promote-unreleased.mjs` does this across N packages at once. Use it like:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/scripts/promote-unreleased.mjs" \
  --version 0.6.X \
  --date 2026-05-21 \
  --packages web-components,web-modules,a2ui/corpus
```

For the manual case (using `Edit`), the exact text-edit pattern:

```diff
- ## [Unreleased]
+ ## [0.6.X] — 2026-05-21
```

That's it. Nothing else changes. The blank line after the heading + the `### Added —` lines below are preserved.

### When promotion is NOT a clean swap

Three cases need extra care:

1. **The substantive package's existing `[vX.Y.Z]` block was already authored as a stub** (e.g. peer cut the release commit early with "no source changes" then continued working). **Promote by replacing** the stub block with the merged `[Unreleased]` content. The v0.6.18 case in `recovery-paths.md` § `[Unreleased]` promotion is the canonical example.

2. **There's no `[Unreleased]` heading but the package DID change** (typically corpus regen — `catalog-a2ui_0_9.json` updated to reflect a yaml change in another package). **Author a fresh `[vX.Y.Z]` block** with `### Changed` (or `### Fixed` if it's a correction) describing the regenerated artifact. See §Authoring below.

3. **`[Unreleased]` has content but it's stale / wrong** (rare — peer authored entries for a different release version, or wrote speculative entries that didn't ship). **Triage with the operator before promoting.**

---

## §Authoring — fresh `[vX.Y.Z]` from scratch

For the substantive-package-changed-but-no-`[Unreleased]` case, write the block above the latest version's heading:

```markdown
## [0.6.X] — 2026-05-21

### Changed
- **<short headline>.** <one-sentence summary of what changed>. <one
  more sentence on why, with file paths if useful>. Closes <ticket /
  symptom>.

### Note
- The headline v0.6.X work shipped in `<other-package>`. See
  `<path-to-other-CHANGELOG>#0X--YYYY-MM-DD` for details.

## [0.6.X-1] — 2026-05-21
```

The `### Note` cross-reference is optional but standard practice when the package's role in the cycle is to be a generated-artifact follow-on of substantive work in another package (e.g. a2ui-corpus catalog regen following web-components yaml changes).

---

## §Stubs — ride-along lockstep

For the 6+ packages that are pure lockstep bumps (no source change), use the template at `assets/templates/stub-changelog.template.md`. The CLI helper `scripts/insert-stub.mjs` inserts this into all the named packages:

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/scripts/insert-stub.mjs" \
  --version 0.6.X \
  --date 2026-05-21 \
  --substantive "<one-line summary> in @adia-ai/<pkg> and @adia-ai/<pkg2>" \
  --xref "packages/web-modules/CHANGELOG.md#0X--YYYY-MM-DD" \
  --packages llm,a2ui/compose,a2ui/mcp,a2ui/retrieval,a2ui/runtime,a2ui/validator
```

The stub block is intentionally short:

```markdown
## [0.6.X] — 2026-05-21

### Maintenance
- **Lockstep version bump only.** No source changes in this package; bumped to maintain the 9-package version coherence enforced by `scripts/release/check-lockstep.mjs`. Substantive v0.6.X work shipped in <SUBSTANTIVE>. See `<XREF>` for details.
```

**Stale stubs are a F-N1 hazard.** A "no source changes" stub on a package that DID change (e.g. a2ui-corpus catalog regenerated but nobody updated its CHANGELOG) makes F-N1 warn for missing keywords. The fix is mode-2 authoring (§Authoring above), not stubbing.

---

## §F-N1 diff-coverage enrichment — the path-keyword discipline

F-N1 (`scripts/release/check-release.mjs --all-pending`) cross-checks the git diff between consecutive package-tags against the CHANGELOG `[VERSION]` block. Its heuristic: for every directory touched in the diff, the CHANGELOG body should mention that directory's keyword.

**Cosmetic warn shape:**

```text
⚠ [warn] diff 'packages/web-components/components/' touched between
  web-components-v0.X.Y-1 → web-components-v0.X.Y but CHANGELOG [0.X.Y]
  doesn't mention 'components'
```

The change IS documented — the entry says "table-ui body cells truncate by default" — but the literal keyword "components" doesn't appear in the body, so the heuristic flags it.

**Fix:** add the path keyword to a natural place in an existing entry. Examples:

- `\`table.yaml\``→`\`components/table/table.yaml\``
- `\`element.js\``→`\`core/element.js\``
- `\`235 chunk JSON files\``→`\`235 JSON files under \`chunks/\``

The keyword goes INSIDE the entry text, ideally inline with a file reference where the path makes the entry MORE accurate (not less). It should NOT be a sidecar parenthetical — that would read as inserted for the gate, not as natural prose.

**Cycle:**

1. Tag, run F-N1, see the warn.
2. Edit the offending CHANGELOG entry.
3. `git add` the CHANGELOG; `git commit --amend --no-edit` (or `--amend` with an updated message).
4. Delete the 10 tags (the SHA moved):

   ```bash
   git tag -d v0.X.Y web-components-v0.X.Y web-modules-v0.X.Y ...
   ```

5. Re-tag at the new HEAD (loop over the 9 per-package + umbrella).
6. Re-run F-N1. Expect 9/9 clean.

**Worth fixing?** Yes for clarity, but the cycle isn't _blocked_ by a single cosmetic warn — F-N1's own message says "review and proceed if intentional." However: do it. The user's "up to standards" directive covers this. By v0.6.21 the peer was authoring entries with full paths from the start (`d8cbbd30c`'s "uses full path so F-N1 gate matches" commit) — that's the goal.

### Real failures vs cosmetic warns

A **real** F-N1 failure is "diff touched `packages/<pkg>/...` and the CHANGELOG `[VERSION]` block doesn't mention the change at all." That means the cycle missed documenting a change — author a CHANGELOG entry, don't just enrich.

A **cosmetic** F-N1 warn is "the change IS documented but the regex didn't match the path keyword." That's the enrichment case above.

Tell them apart by **reading the CHANGELOG entry**: does any bullet describe the touched files (by component name, by what the change does)? If yes → cosmetic → enrich. If no → real → author.

---

## §Dating — local-time vs UTC

The AdiaUI repo's CHANGELOG dates are written in YYYY-MM-DD format without timezone. Today's date is what the operator considers "today" — typically local-time Pacific.

The repo has historically mixed dates (v0.6.10 was 2026-05-21 due to UTC rollover at cut time; v0.6.11 came back to 2026-05-20). Don't try to enforce strict consistency retroactively — too much churn for a cosmetic alignment. **For NEW cycles**, use the local date the cycle ships in.

If the operator and the runtime disagree on date (e.g. a `<system-reminder>` says today is 2026-05-21 but local clock says 2026-05-20), use the system reminder's date. It's the authoritative current date.

---

## §Markdown anchor convention

GitHub auto-generates anchors from headings. The convention `[X.Y.Z] — YYYY-MM-DD` slugifies to `XYZ--YYYY-MM-DD` (brackets/dots stripped; em-dash + spaces → double hyphen).

When a stub references another package's `[VERSION]` block:

```markdown
See `packages/web-modules/CHANGELOG.md#0621--2026-05-21` for details.
```

The anchor `#0621--2026-05-21` corresponds to `## [0.6.21] — 2026-05-21`. The `insert-stub.mjs` helper computes this automatically; for manual authoring, the formula is:

- Strip `[`, `]`, `.` from the version
- Replace `—` (em-dash + space) with `-` (en-hyphen)
- Lowercase

So `[0.6.21] — 2026-05-21` → `0621--2026-05-21` (the leading `--` comes from the em-dash being replaced by one hyphen + the space being replaced by another).

---

## §What to put in `### Added` / `### Changed` / `### Fixed` / etc

Keep a Changelog defines 6 categories:

- **Added** — for new features
- **Changed** — for changes in existing functionality
- **Deprecated** — for soon-to-be-removed features (deprecation notices; the feature still works)
- **Removed** — for now-removed features (the feature is gone; was deprecated previously)
- **Fixed** — for any bug fixes
- **Security** — in case of vulnerabilities

In the AdiaUI repo, **Added** and **Fixed** dominate. **Changed** is used for behavior changes that aren't fixes (e.g. default-value changes like the v0.6.13 `<admin-shell>` default-mode change to `"rounded borderless"`). **Removed** is rare in the 0.6.x line — v0.6.21's FEEDBACK-37 retraction was documented as `### Fixed` (spurious warn removed) rather than `### Removed` because the removal fixed a defect.

Two custom AdiaUI conventions worth knowing:

- **`### Maintenance`** — used for pure lockstep stubs (no source change). The Keep-a-Changelog spec doesn't have this; it's an AdiaUI extension that makes "this is just a bump" obvious to readers.
- **`### Docs`** — used for documentation-only changes. Standard practice in some Keep-a-Changelog dialects.

---

## §Entry style — what makes a good bullet

Across 20+ cycles, the entries that age well share these traits:

1. **Bold-prefix one-line headline** — the title-cased headline of the change. The reader sees this even when scrolling fast.
2. **Why → what → file paths** — explain the motivation (1 sentence), the mechanism (1 sentence), and the files touched (inline backtick).
3. **`Closes/Fixes <ticket>`** — when a feedback ticket is closed, name the ticket ID (FEEDBACK-NN). This is what `release-notes` cross-references later.
4. **Pre/post code block** — when the change has a consumer-facing API or markup difference, show before/after. The v0.6.13 `<admin-shell>` default-mode entry's "Opt-out matrix" code block is the canonical example.
5. **Inline file path** — `\`components/table/table.yaml\``(not just`\`table.yaml\``). F-N1 likes it; readers like it too.

Avoid:

- Vague verbs ("improved", "tweaked") without specifics.
- Reference-by-ticket-only — always describe what the code does, not just "fixes FB-NN".
- Future tense ("will support") — entries are written about shipped work.

---

## §When this reference is "done v1"

- Every cycle's `[Unreleased]` → `[VERSION]` promotion completes with no operator improvisation beyond `promote-unreleased.mjs`.
- F-N1 warns are categorized cosmetic vs real on first inspection with no false positives.
- Stale stubs are zero in the next 3 cycles.
- The path-keyword discipline holds at authoring time — no enrichment pass needed (peer adopted it by v0.6.21; this skill codifies the same).

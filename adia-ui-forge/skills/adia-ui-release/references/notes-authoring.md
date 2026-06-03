# `notes-authoring.md` — Slack + GH-release single-version notes

> Loaded by mode 9 (Authoring discipline only) and by mode 1 Step 10 (GH releases). Covers both the per-version GH-release body and the Slack-flavored team announcement.

The AdiaUI repo has two single-version note formats:

1. **GH release body** — markdown, attached to each per-package tag's GH Release (created via `gh release create <pkg>-vX.Y.Z --notes-file ...`). All 9 packages get the same body.
2. **Slack release post** — markdown, intended to be pasted into #releases or similar. Shorter, more conversational, has the `npm install` snippet at the top.

Multi-version rollup notes are a separate format — see `rollup-notes.md`.

---

## §The GH release body — single version

Audience: external consumers reading the GH Releases page. Substantive

- practical. Each entry should answer "what shipped" + "what do I do with it."

**Standard structure (~80–200 lines per release):**

```markdown
## vX.Y.Z — <one-line tagline>

9-package lockstep **PATCH** cut. <One sentence on the scope.>

<Optional: a > heads-up callout if there's a behavior change or
breaking thing.>

### `@adia-ai/<substantive-pkg>`

- **<Bold-prefix headline>.** <Why → what → file paths.> Closes <FEEDBACK-NN>.
- **<Bold-prefix headline>.** <Same shape.>

### `@adia-ai/<other-substantive-pkg>`

- ...

### Ride-along stubs

`@adia-ai/<pkg1>`, `@adia-ai/<pkg2>`, ... — version bump only.

### Verification

- `check:lockstep` OK at `X.Y.Z / ^X.Y.0`
- **N/N vitest** across NN files · typecheck clean
- `components --verify` clean (NN files) · `verify:traits` 56/56
- `check:demo-shells` clean · `check:lightningcss-build` clean (NN files)
- `verify:corpus` 0/0 · `check:embeddings-fresh` OK
- `smoke:engines` green · `smoke:register-engine` 11/11 · `eval:diff zettel` cov=N% avg=N · `check:links` NNNN clean

### Install

\`\`\`bash
npm i @adia-ai/web-components@X.Y.Z @adia-ai/web-modules@X.Y.Z
\`\`\`
```

**Shape rules:**

- **Open with the tagline + one-sentence scope** — no preamble, no "we're excited to announce." Readers came to find out what's in it.
- **Group by package** — `### @adia-ai/<pkg>` headings. Use the `@adia-ai/` prefix; it's the npm name + the search key.
- **Bold-prefix every bullet** with the headline. Then 1–3 sentences: why → what → files. Inline backtick file paths.
- **Cite tickets by ID** — `FEEDBACK-NN` (or `FB-NN`). Match the CHANGELOG entry's citation style for that cycle.
- **Show before/after** when a change has consumer-facing markup difference. Use fenced code blocks.
- **Stubs go in a one-line `### Ride-along stubs`** — list the packages by name. Don't repeat the "lockstep version bump only" text — readers see the same per-cycle.
- **Verification section** is identical-style across cycles. Paste the gate output from your pre-flight. The repetition is a feature — readers learn what "all green" looks like.
- **Install matrix** at the bottom — **npm + CDN, both packages** (same mandate as the Slack post). npm: always `@adia-ai/web-components` + `@adia-ai/web-modules` (the universal entry points). CDN: a jsdelivr block pinned `@0.X` — `web-components@0.X/dist/web-components.min.{css,js}` + the `web-modules@0.X/dist/everything.min.js` kitchen-sink. Other packages added if substantive in the cut.

**Anti-patterns:**

- Marketing language. The notes are technical.
- Vague verbs. "Improved" / "polished" / "tweaked" without specifics is empty.
- Missing file paths. Inline backticks like `packages/<pkg>/...` let readers grep.
- Long preambles. Maximum 1 short paragraph before the per-package sections.

### Template — copy this verbatim and fill in

The template lives at `assets/templates/gh-release-notes.template.md` (Phase 2). It maps to a minimal cycle output (~80 lines for a stub-heavy release like v0.6.17, ~200 lines for a substantive cycle like v0.6.18).

For now, the most recent cycles' release notes are reference templates:

- `/tmp/release-v0.6.21.md` — table-ui truncate + FEEDBACK-37 retraction
- `/tmp/release-v0.6.20.md` — claims-ui-v5 + admin-entity-item
- `/tmp/release-v0.6.19.md` — claims-ui-v4 batch + corpus remediation

---

## §The Slack release post

Audience: internal team in #releases or similar. Shorter, more conversational, with the `npm install` snippet at the top so readers can copy-paste immediately.

**Standard structure (~40–80 lines):**

```markdown
🚀 **AdiaUI vX.Y.Z** is out — <one-line tagline>

\`\`\`bash
npm i @adia-ai/web-components@X.Y.Z @adia-ai/web-modules@X.Y.Z
\`\`\`

9-package lockstep PATCH cut. <One sentence on scope.>

## <emoji> `@adia-ai/<substantive-pkg>` — <subsection-headline>

<2–4 sentences. The thing that matters.> Closes <FEEDBACK-NN>.

\`\`\`html
<example markup if useful>
\`\`\`

## <emoji> Ride-along

<short>

## ✅ Verification

<one-line summary of the gate roster status>

## 📚 Links

- GH Releases: https://github.com/adiahealth/gen-ui-kit/releases (filter `vX.Y.Z`)
- Live demos: https://ui-kit.exe.xyz/site/playground/gen-ui
```

> **Every `https://ui-kit.exe.xyz/site/<route>` URL cited in notes MUST be verified against `site/sitemap.json` first** (`grep '"path": "/site/…"'`). The docs site is an SPA — unmatched routes return HTTP 200 but render blank, so a curl check won't catch a wrong URL. There is no `/site/gen-ui/` route; the Gen UI Canvas is `/site/playground/gen-ui`. `<theme-panel>` has no standalone page — it's the palette popover on every page. (v0.7.4 incident: both cited URLs were blank.)

**Shape rules:**

- **Open with the rocket emoji + bold version + tagline.** Slack renders this prominently.
- **Install matrix immediately under the header (MANDATORY — npm + CDN, both packages).** Every note carries the full install surface, in this order:
  1. **npm** — `npm i @adia-ai/web-components@X.Y.Z @adia-ai/web-modules@X.Y.Z` (BOTH packages, never just web-components).
  2. **CDN** — a jsdelivr block pinned to the `@0.X` minor-range: `web-components@0.X/dist/web-components.min.css` (CSS) + `web-components@0.X/dist/web-components.min.js` (primitives JS), plus the `web-modules@0.X/dist/everything.min.js` kitchen-sink as the all-in-one `<script>` alternative. (CDN bundles ship since v0.6.29/0.6.30.) Operator standard since 2026-05-31. Canonical shape: `.brain/release-notes/0.7.0-release-notes.md`.
- **Section emojis** — `🔷` (substantive feature), `🛠️` (DX fix), `🎨` (visual), `🧹` (cleanup), `⚠️` (breaking / behavior change), `✅` (verification), `📚` (links). Slack renders these natively.
- **Skip the per-package grouping** when there's only 1 substantive package. Group by feature instead.
- **Code blocks for examples** — Slack's modern rich-text composer (since 2020) renders standard markdown fenced code blocks. Memory: `feedback_slack_renders_standard_markdown` — `-` bullets + `[text](URL)` links work natively; legacy `•` + `<URL|text>` mrkdwn isn't needed.
- **Links section at the bottom** — GH Releases + live demos at minimum.

**Anti-patterns:**

- Marketing speak ("we're thrilled..."). Engineers read this.
- Long verification sections. One line is enough for Slack; details live in the GH release.
- Multi-paragraph "context" sections. If the tagline + 2 sentences don't cover it, the change is too complex for a single Slack post — link to the GH release or a longer write-up.

### Where to put the notes

**Canonical home: `.brain/release-notes/{version}-release-notes.md`** (committed with the cycle's ledger — durable repo artifact, not `/tmp`, and not `.brain/notes/` which is for working notes/plans). Open with YAML frontmatter per `.brain/release-notes/README.md`:

```yaml
---
title: AdiaUI v{version} — release notes
version: {version}
topic: release-notes
status: final
created: <ISO-8601 UTC, from `date -u +%Y-%m-%dT%H:%M:%SZ`>
last_edited: <same; bump on edit>
author: adia-ui-release ({model})
---
```

The Slack post and GH-release body are **derived from** this file (strip frontmatter for the GH body — see `cycle-happy-path.md` §Step 10). If the operator wants a separate Slack-flavored draft, `/tmp/release-vX.Y.Z/slack.md` is fine for that scratch copy, but the `.brain/notes/` file is the source of record. The operator copy-pastes from whichever they prefer. The `release-pack.mjs` orchestrator (Phase 3) will support a `--push-slack <channel>` flag for direct send, but the default remains draft-to-file — the operator owns the announcement decision.

---

## §The verification section — what to actually include

Standard verification block (paste from the cycle's pre-flight output):

- `check:lockstep` line
- `test:unit` count
- `typecheck` (one-word "clean")
- `components --verify` (file count)
- `verify:traits` (`56/56`)
- `check:demo-shells` (shell count)
- `check:lightningcss-build` (CSS file count)
- `verify:corpus` (`0/0`)
- `check:embeddings-fresh` (`OK`)
- `smoke:engines` + `smoke:register-engine`
- `eval:diff zettel` (cov + avg)
- `check:links` (file count)

For a substantive cycle, also include any NEW gates added in this cycle (e.g. v0.6.12 added `verify:no-legacy-shell-shapes`; first cycle shipping a new gate calls it out).

Skip optional gates (`check:card-structure`, `check:drawer-structure`, etc.) unless one of them was the lesson of the cycle.

---

## §Cross-references — when to cite siblings

A single-version note may need to reference:

- **A previous version** when the current cycle retracts / iterates on it. Example: v0.6.21 retracts FEEDBACK-37 from v0.6.20 — the v0.6.21 note has a heads-up paragraph naming v0.6.20.
- **A future version** when something is deferred. Less common; use sparingly.
- **A companion plugin/skill version** when the cycle bundles a tooling update alongside the package cut. Format: "Companion: `<companion-plugin>` **vX.Y.Z** — `<one-line>`."
- **An ADR** when the cycle ratifies an architectural decision. Format: "Post-mortem at ADR-NNNN." Example: v0.6.21 → ADR-0033.

---

## §What NOT to put in the notes

- Internal-only ticket fields (assignee, status before/after, etc.).
- Implementation details that don't affect consumers (file rename inside a package, refactor that didn't change API).
- "Coming soon" announcements about future versions. Notes describe shipped work.
- Profanity, jokes, or off-topic content. Notes are a permanent artifact attached to a tag.

---

## §When this reference is "done v1"

- The `gh-release-notes.template.md` and `slack-release.template.md` templates land in `assets/templates/`.
- The next 3 cycles' notes are authored from the template + the per-cycle CHANGELOG content with no operator improvisation beyond filling in version-specific details.
- The Slack post copy-paste shape works in Slack's rich-text composer with zero `mrkdwn` (legacy) overrides.

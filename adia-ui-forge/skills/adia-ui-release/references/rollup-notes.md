# `rollup-notes.md` — multi-version retrospective notes

> Loaded by mode 5 (Author rollup release notes). Companion to `notes-authoring.md` (single-version notes).

A rollup release note covers a RANGE of versions (e.g. v0.6.8 → v0.6.16, v0.6.16 → v0.6.21). Audience: someone catching up on multiple releases at once — typically external consumers who skipped a few cuts, or internal teammates returning from a holiday, or a Slack announcement for a milestone window.

Two rollup formats have shipped from this skill's lineage:

1. **`/tmp/release-v0.6.8-v0.6.16/rollup.md`** (9 PATCH cuts) — organized by **narrative arcs** (3 themes), with per-version bullet-summaries inside each arc.
2. **`/tmp/release-v0.6.16-v0.6.21/rollup.md`** (6 PATCH cuts, skill-centric) — opened with the **skill as headline framing**, then per-version package work as substrate. Different headline, same per-version-bullet pattern below.

Both share a common skeleton (this template) but the FRAMING is what makes them distinct.

---

## §The 5-section skeleton

```markdown
🚀 **AdiaUI vA.B.C → vX.Y.Z** — <one-line tagline>

\`\`\`bash
npm i @adia-ai/web-components@X.Y.Z @adia-ai/web-modules@X.Y.Z
\`\`\`

<2–4 sentences setting up: how many releases, what the window is
about, what's load-bearing across all of them (e.g. "internal deps
held at ^0.6.0 throughout").>

---

## 🧵 <Framing section — pick ONE>

<This is the headline. It's the through-line that connects the N
releases. See §Framing options below.>

---

## 📦 Per-version breakdown

### vA.B.C — <tagline>

<3–5 bullets covering substantive work. Inline backtick file paths.
Reference FEEDBACK-NN closures. Cite the substantive packages.>

### vA.B.D — <tagline>

<same shape>

... (one block per version)

---

## ⚠️ <Optional: behavior changes worth knowing>

<Table summarizing breaking / behavior changes across the window
with opt-out paths. Use sparingly — most PATCH cuts have none.>

---

## ✅ Verification baseline (held across all N cuts)

<one-paragraph summary: vitest count growth, gate roster status,
eval floor held, etc.>

## 📚 Links

- GH Releases: <URL>
- Live demos: <URL>

---

**<Closing paragraph — name what the window accomplished as a whole.
Connect to the framing section.>**
```

---

## §Framing options — pick ONE for the headline

A rollup is more than a list of releases — it's a STORY. Pick the headline framing that matches the window:

### Option A — "The arcs" (chronological + thematic)

When the window has 2–4 distinct thematic strands. Each strand gets a short subsection naming the versions that contributed.

Example (v0.6.8 → v0.6.16):

> ## 🧵 The three arcs
>
> **1. Toolchain + build-time correctness** (v0.6.8 / v0.6.9) HTML-parser and CSS-spec traps that broke real consumer builds.
>
> **2. Consumer DX cliffs** (v0.6.10 / v0.6.11 / v0.6.15) Cold-start failure modes closed with diagnostics or opt-in carve-outs.
>
> **3. The `<admin-shell>` composition arc** (v0.6.12 → v0.6.16) A five-release refinement of the admin-shell tier.

Best when: the window is mid-cycle, no single dominant theme.

### Option B — "The headline event" (one big thing)

When the window IS one big thing surrounded by supporting work. A skill-graduation window (v0.6.16 → v0.6.21) used this — the headline was a companion consultant skill graduating to a major version; the package releases are substrate.

Example:

> **The headline of this window is not the package releases — it's the skill.** The companion consultant skill (v2.10.0 → v2.20.8) is now the official autonomous-consultant tooling for working with the framework in any LLM-driven coding harness. The package releases that follow are the substrate work that supports it.

Best when: there's a milestone (skill graduation, ADR ratification, substrate completion). The package releases support a larger arc.

### Option C — "Net deltas"

When the window's main story is what consumers SEE differently end- to-end. Like a `git diff vA.B.C..vX.Y.Z` rendered as prose.

Example shape:

> ## 🧵 What changed for consumers
>
> - **New primitives:** `<admin-entity-item>` (v0.6.20), `<list>`
> - **New APIs:** `stat-ui loading`, `table-ui loading` (v0.6.18), `table-ui row-click` (v0.6.20), `<list>`
> - **Breaking-ish:** `<admin-shell mode>` default changed v0.6.13 (rounded borderless); page-header bg iterated v0.6.14 → v0.6.16 → v0.6.20 (canvas-2 → canvas-1 → canvas-0)
> - **Retired:** legacy `<main>` + `[data-content-*]` admin-shell shape (v0.6.12)

Best when: the window includes a MINOR cut (cumulative change matters) or when a consumer is migrating across a big gap.

---

## §Per-version block — sub-template

Each version block has the same shape regardless of framing:

```markdown
### vN.M.X — <tagline>

`@adia-ai/<pkg>`:
- **<bold-prefix bullet>.** <One-sentence why → what. File paths
  inline.> Closes <FEEDBACK-NN>.
- **<bold-prefix bullet>.** <same shape>

`@adia-ai/<other-pkg>`:
- <bullets>

Companion: `<companion-plugin>` **vX.Y.Z** — <one-line> (if applicable)
```

**Length per version**: 3–5 bullets if the version was substantive; 1–2 bullets if it was small. Stub-only versions get a single sentence at most ("v0.6.17 shipped only an admin-sidebar collapse fallback — see GH release for details").

**Skip ride-along stubs** in a rollup. The reader knows lockstep exists; mentioning 6 packages did "no source change" 6 times is noise.

---

## §The "behavior changes worth knowing" table

Use a 3-column markdown table when the window has 2+ behavior changes that consumers should track:

```markdown
| Version | Change | Opt-out / migration |
|---|---|---|
| **v0.6.12** | Legacy `<admin-shell>` CSS bridges removed | Migrate to the 10-tag bespoke composition (zero audited consumers affected) |
| **v0.6.13** | Bare `<admin-shell>` defaults to `mode="rounded borderless"` | Set `mode=""` for the flat legacy chrome |
```

Skip the table if the window has zero behavior changes. Don't pad it with non-changes.

---

## §Verification — one paragraph, not the full table

For a single-version note (`notes-authoring.md`), the verification section lists every gate's status. For a rollup, that's too much — compress to a paragraph:

```markdown
## ✅ Verification baseline (held across all N cuts)

- **NNNN/NNNN vitest** across NN files at vX.Y.Z (up from NNNN at the
  start of the arc — net +NN from <reasons>)
- `check:lockstep` OK · `components --verify` clean · `verify:traits` 56/56 · typecheck clean
- `check:demo-shells` clean · `check:lightningcss-build` clean (NN CSS files)
- `verify:corpus` 0 errors / 0 warns · `check:embeddings-fresh` OK
- `smoke:engines` green · `smoke:register-engine` 11/11 · `eval:diff zettel` cov=N% avg=N (baseline-identical across the window)
- F-N1 release trip-wire 9/9 per-package clean at every cut
```

Show the **growth** (test count delta, new gate counts) — that's the window's velocity signal.

---

## §The closing paragraph

The last paragraph is the "what did this window accomplish." It echoes the framing section but as a conclusion.

Example (v0.6.16 → v0.6.21, skill-centric framing):

> **The v0.6.16 → v0.6.21 window is the maturation of the companion consultant skill from a documentation skill (v2.x.0) into the autonomous consultant posture (v2.20.8) — with a track record across two consumer cold-start batches (39 tickets between them, all triaged through the skill's own ticket pipeline) and an ADR ratifying the Light-DOM substrate stance the skill teaches first. The package releases are the substrate that backs every claim the skill makes.**

Tight, evocative, names the window's _accomplishment_ (not just its contents).

---

## §Where to put the rollup

Save to `/tmp/release-vA.B.C-vX.Y.Z/rollup.md`. The operator copy-pastes where they want it — Slack #releases for an internal announcement, the GH Releases page as a "milestone" body, a CHANGELOG ROLLUP doc in the repo, or a blog post.

If the rollup is **announcement-grade** (skill graduation, MINOR cut, ADR ratification), consider also publishing it to a permanent location (`docs/announcements/` or similar). Coordinate with the operator.

---

## §When this reference is "done v1"

- The `rollup-notes.template.md` template lands in `assets/templates/`.
- The next 2 rollup notes are authored from the 5-section skeleton + one of the 3 framing options with no operator improvisation beyond filling in window-specific details.
- Each framing option has at least one example in `assets/case-studies/` (Phase 3) so future authors see the shape applied to a real window.

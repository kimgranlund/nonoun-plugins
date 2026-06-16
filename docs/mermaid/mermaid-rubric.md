---
date: 2026-06-16
status: draft
version: "0.1.0"
target: mermaid@11.15.0 (the catalog corpus-reader pin)
---

# Mermaid Diagram Quality — Rubric

Scores a single Mermaid diagram (as authored in a corpus Markdown fence) for whether it is the **right diagram, validly expressed, that renders in the target reader, legibly and accessibly, without depending on the host.** Companion to **[advanced-mermaid-reference.md](advanced-mermaid-reference.md)** — the reference tells you the syntax; this rubric tells you whether a given diagram is good.

Two dimensions are **`[gate]`** (a fail is blocking — the diagram won't render or will mislead); four are **`[review]`** (judgment). Score each 1–5 with the diagram as evidence.

---

## §The Problem

A diagram is not prose with a picture bolted on — it is a claim about structure, rendered by a specific engine under specific constraints. Three independent ways it fails: it **doesn't render** (wrong keyword, a type newer than the pin, a feature the strict reader denies); it **renders but misleads** (wrong diagram type for the relationship, or so dense no one can read it); or it **renders here but not there** (depends on host-side config or interactivity that doesn't travel in a Markdown fence). The first is the most common and the most embarrassing — a `sankey` that should have been `sankey-beta`, an `architecture-beta` leaning on an iconify pack the reader never registered. Markdown preview says nothing about any of this; the cost is a broken diagram shipped into a corpus.

---

## §First Principles

1. **Right type for the relationship.** Flow ≠ hierarchy ≠ overlap ≠ time ≠ causation ≠ value-chain. The diagram type is the first and largest decision.
2. **Renders in the target, or it doesn't exist.** Validity is judged against `mermaid@11.15.0` + `securityLevel: "strict"` + no host config — not against the Live Editor's latest build.
3. **Legible at a glance.** A diagram past a complexity threshold conveys *less* than the table it replaced.
4. **Accessible by construction.** `accTitle`/`accDescr` set; meaning never carried by color alone.
5. **Portable and deterministic.** What travels in the fence is all there is; layout shouldn't reshuffle between renders of the same source.

---

## §The Rubric

### M1 — Diagram-type fit `[review]`

Is this the diagram type that matches the relationship being communicated?

| Score | Evidence |
| --- | --- |
| **5** | The type is the natural fit: flow→`flowchart`/`sankey-beta`, sequence→`sequenceDiagram`, schema→`erDiagram`, time→`gantt`/`timeline`, journey→`journey`, board→`kanban`, overlap→`venn-beta`, causation→`ishikawa-beta`, strategy→`wardley-beta`, deployment→`architecture-beta`, event-sourcing→`eventmodeling`. A reader instantly grasps the intended structure. |
| **4** | Good fit; a second type would arguably serve as well. |
| **3** | Workable but not ideal — e.g. a `flowchart` faking a sequence, or an ER relationship drawn as a generic graph. |
| **2** | The type fights the content — overlap forced into a tree, time forced into a flowchart. |
| **1** | Wrong type entirely; the diagram obscures the relationship it should reveal. |

**Go deeper:** the reference §2 matrix + per-type "Purpose". **Test:** name the relationship in one word (flow/hierarchy/overlap/time/causation/value-chain); does the chosen keyword's purpose match it? Mismatch = M1 ≤ 2.

---

### M2 — Syntax validity & version-safety `[gate]`

Does it parse on `mermaid@11.15.0` with the **exact** keyword, using only features present in that release?

| Score | Evidence |
| --- | --- |
| **5** | Exact keyword incl. any `-beta` suffix (`sankey-beta`, `architecture-beta`, `venn-beta`, `ishikawa-beta`, `wardley-beta`, `treeView-beta`; **no** suffix on `kanban`/`eventmodeling`/`journey`/`gantt`/`erDiagram`). Every construct exists in 11.15.0. Parses clean. |
| **4** | Parses; a minor non-blocking quirk (an over-cautious quote, a deprecated `%%{init}%%` that still works). |
| **3** | Parses only after a small fix the author missed (one mis-quoted label). |
| **2** | A construct post-dates 11.15.0, or a label's special characters break parsing — renders only after real edits. |
| **1** | Bare beta keyword (`sankey`, `architecture`, …) or a type/feature not in 11.15.0 → hard syntax error; nothing renders. |

**Go deeper:** reference §1.5, §2, §5. **Test (mechanical):** does the first line carry the exact keyword from the §2 matrix, and does a bake (`build-sitemap.py --bake`) render it without a `Syntax error in text`? Wrong/missing `-beta`, or a post-11.15.0 feature = **M2 fails (≤2)**.

---

### M3 — Renders in the target reader `[gate]`

Does it render correctly under the reader's `securityLevel: "strict"` and with **no host-side configuration**?

| Score | Evidence |
| --- | --- |
| **5** | No reliance on interactivity (`click`/`call`), no HTML in labels, no iconify packs (architecture uses only the 5 built-in icons), no host-only JS config (`sankey`/`kanban` width/colors/`ticketBaseUrl`). What renders in a bake is the full intended diagram. |
| **4** | Renders fully; one cosmetic nicety would have needed host config but its absence doesn't change meaning. |
| **3** | Renders, but a non-essential affordance is silently dropped (a `ticket:` shows as text because `ticketBaseUrl` is host-config). |
| **2** | A meaning-bearing element fails under strict — an architecture icon-pack glyph missing, an HTML-formatted label shown as raw `<br/>`. |
| **1** | The diagram's point depends on a click, a hyperlink, or host config the reader can't provide — it's broken or inert here. |

**Go deeper:** reference §1 (the six-point contract). **Test:** scan for `click`, `<br/>`/`<b>`/`<a` in labels, non-built-in architecture icons, and host-config dependence (`ticketBaseUrl`, JS `sankey`/`kanban` options). Any meaning-bearing dependence on them = **M3 fails (≤2)**. (Render in a bake to confirm.)

---

### M4 — Legibility & cognitive load `[review]`

Can a reader grasp it at a glance, or has it become a wall of nodes?

| Score | Evidence |
| --- | --- |
| **5** | Bounded and scannable: roughly ≤ ~15–20 nodes / ≤ ~25 edges; sensible direction (`TD`/`LR`); labels short and consistent; sections/groups used to chunk. Conveys *more* than the equivalent prose/table. |
| **4** | Readable; slightly busy in one region. |
| **3** | Dense — readable with effort; would benefit from splitting or grouping. |
| **2** | Overcrowded: too many crossing edges or nodes to follow; a table would communicate better. |
| **1** | Illegible hairball; the diagram hides the structure. |

**Go deeper:** reference §5. **Test:** count nodes/edges and try to trace the main path in 5 seconds. Can't → M4 ≤ 2; consider splitting into two diagrams or using a `section`/`group`.

---

### M5 — Accessibility `[review]`

Is the diagram usable beyond a sighted glance at color?

| Score | Evidence |
| --- | --- |
| **5** | `accTitle:` and `accDescr:` set with a meaningful summary; no meaning carried by color alone (labels/shapes/text also distinguish); contrast respects the reader's light/dark theme rather than hard-coded hex that fails one mode. |
| **4** | `accTitle`/`accDescr` present; one element leans a bit on color. |
| **3** | Missing `accDescr`, or color is a primary (not sole) channel. |
| **2** | No accessible title/description and color is the main differentiator. |
| **1** | Color-only encoding, no text alternative — opaque to a screen reader or in monochrome. |

**Go deeper:** reference §3 "Accessibility". **Test:** are `accTitle`/`accDescr` present, and does the diagram still parse meaning if rendered grayscale? No/No → M5 ≤ 2.

---

### M6 — Portability & determinism `[review]`

Will it render the same way for the next person, in the next corpus, on the next bake?

| Score | Evidence |
| --- | --- |
| **5** | All configuration is in-fence (frontmatter `config:` / inline `style`), not host JS. Layout is deterministic, or force-directed layout (architecture) is pinned via `randomize`/fcose knobs. No hard-coded theme that fights the reader. Self-contained — copy-paste into any corpus and it renders identically. |
| **4** | Portable; one cosmetic setting assumes a default that usually holds. |
| **3** | Renders portably but layout can reshuffle between renders (unpinned force-directed) or a hard-coded theme clashes in one mode. |
| **2** | Depends on a host config or external icon pack to look right elsewhere. |
| **1** | Only renders correctly in the exact environment it was authored in. |

**Go deeper:** reference §1.4, §1.6. **Test:** strip everything but the fence and render in a clean bake — same result? Force-directed type pinned? Host-config-dependent = M6 ≤ 2.

---

## §Anti-patterns

### AP-M1 — The bare-beta keyword

**Symptom:** `sankey` / `architecture` / `venn` / `ishikawa` / `wardley` / `treeView` without `-beta` → `Syntax error in text`, nothing renders (M2 ✗). **Root cause:** copying the mermaid.ai docs, which show the aspirational un-suffixed form. **Correction:** use the exact `-beta` keyword from the §2 matrix; render in a bake.

### AP-M2 — The click-dependent diagram

**Symptom:** a `gantt`/`flowchart` whose value is in `click … href` links, inert under the reader's `strict` (M3 ✗). **Root cause:** authored in the Live Editor with `loose`. **Correction:** put the link in surrounding prose; let the diagram carry structure, not navigation.

### AP-M3 — The icon-pack architecture diagram

**Symptom:** `architecture-beta` using `logos:aws-…`/iconify glyphs that render blank in the reader (M3 ✗). **Root cause:** iconify packs need a host `registerIconPacks()` a fence can't call. **Correction:** use the five built-in icons (`cloud`/`database`/`disk`/`internet`/`server`) for portable corpus diagrams.

### AP-M4 — The wall of nodes

**Symptom:** 40 nodes, crossing edges, unreadable (M4 ✗). **Root cause:** one diagram doing the job of three. **Correction:** split by `section`/`group` or into multiple diagrams; or use a table where flow isn't the point.

### AP-M5 — Color as the only channel

**Symptom:** meaning encoded purely in fill color, no `accDescr`, illegible in grayscale or to a screen reader (M5 ✗). **Correction:** add `accTitle`/`accDescr`; differentiate by label/shape/text too.

### AP-M6 — The host-config diagram

**Symptom:** a `sankey-beta`/`kanban` that looks right only with JS-side width/colors/`ticketBaseUrl` (M6 ✗) — degrades silently in another corpus. **Correction:** move what you can into in-fence frontmatter `config:`; accept reader defaults for the rest.

---

## §Hard Tests

1. **The keyword test** (M2): does line 1 carry the exact `-beta`-correct keyword, and does a bake render without `Syntax error in text`?
2. **The strict test** (M3): any reliance on `click`, HTML-in-label, iconify packs, or host JS config? → it won't survive the reader.
3. **The five-second test** (M4): can a reader trace the main structure in five seconds, or is it a hairball?
4. **The grayscale + screen-reader test** (M5): `accTitle`/`accDescr` present, and meaning survives without color?
5. **The clean-bake test** (M6): strip to the fence, render in a fresh corpus — identical result, deterministic layout?
6. **The type test** (M1): name the relationship in one word — does the chosen diagram type match it?

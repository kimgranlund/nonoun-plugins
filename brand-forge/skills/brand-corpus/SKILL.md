---
name: brand-corpus
description: >
  Canonical structure and stewardship for a brand's documentation — the layered 01-foundation …
  08-evaluation corpus, the two output conventions (flat double-hyphen filenames for a Claude
  Project; nested folders for a filesystem), corpus maturity stages 0–6, and the read-before-write
  discipline that keeps the corpus coherent. Use whenever organizing, structuring, naming, or
  auditing brand files. Triggers on "brand corpus", "organize brand files", "brand documentation
  structure", "set up brand docs", "where does this brand file go", "brand file naming".
  The brand-corpus MCP is the live-data complement to this layout.
---

# Brand Corpus

A brand is only as coherent as the documents it is stored in. This skill defines **where every brand artifact lives**, **how it is named**, and **how it grows** — so the corpus stays a single source of truth instead of a folder of contradictions.

This file is the table of contents; the full layout, layer contents, and per-stage detail live in [`references/corpus-architecture.md`](references/corpus-architecture.md).

## The canonical layered structure

Eight numbered layers, ordered so each depends only on the ones above it. Foundation first; expression descends from it; evaluation closes the loop.

```text
01-foundation     the load-bearing strategy (root, position, POV, transformation, principles)
02-positioning    territories, category design, competitive archaeology
03-identity       logo system, marks, the visual idea
04-expression     type, color, layout, imagery, motion — the expression system
05-voice          tone, naming, copy principles, worked examples
06-product         the brand as experienced in the product / UX
07-guidelines     governance, usage rules, do/don't, the rules of coherence
08-evaluation     audits, rubric scores, council reviews, decisions
```

The numbering is **load-order**, not preference: nothing in 03–06 is valid unless it descends from 01. An identity with no foundation above it is decoration. → Full per-layer contents in [`references/corpus-architecture.md`](references/corpus-architecture.md).

## Two output conventions — never mixed

A corpus is emitted in exactly **one** of two shapes, chosen by destination. **Never mix them** within a single corpus — a half-flat, half-nested corpus breaks both retrieval and the human's mental model.

|  | **Flat** (Claude Project) | **Folder** (filesystem) |
| --- | --- | --- |
| **Where** | Claude Project knowledge — no directories | A repo / disk |
| **Shape** | One flat list of files | Nested `01-foundation/…` directories |
| **Naming** | **Double-hyphen** encodes the layer: `01-foundation--the-position.md` | Path encodes the layer: `01-foundation/the-position.md` |
| **Why** | Projects have no folders; the `NN-layer--` prefix preserves order and grouping in a flat namespace | Folders are native; the path _is_ the layer |

**The rule:** decide the destination first, pick the convention, and hold it for the whole corpus. If you find both conventions present, that is a corpus defect — reconcile to one before adding anything. Migration between the two is mechanical (`01-foundation--x.md` ⟷ `01-foundation/x.md`) and tooled: **`bin/corpus-migrate <corpus> --to {flat|folder}`** detects the shape, refuses a mixed corpus, and renames every layer asset (dry-run by default). The per-layer maturity manifest + the completeness audit checklist are in [`references/corpus-architecture.md`](references/corpus-architecture.md) § Extension point.

## Corpus maturity (stages 0–6)

A corpus is not built all at once; it matures. Knowing the stage tells you what to build next and what not to fake.

| Stage | State | What exists |
| --- | --- | --- |
| **0** | Empty | Nothing — or scattered, unstructured notes. |
| **1** | Seed | The 3-page minimum-viable **foundation** (01) only. |
| **2** | Positioned | Foundation + positioning territories (01–02). |
| **3** | Identified | Visual identity exists and descends from strategy (01–03). |
| **4** | Expressed | A working expression system — type/color/layout/voice (01–05). |
| **5** | Operational | Lives in the product, with guidelines a stranger can follow (01–07). |
| **6** | Stewarded | Closed loop: audits and council reviews feed back into 01 (01–08). |

**Do not skip stages by faking artifacts.** A stage-5 guidelines doc on a stage-1 foundation is the classic failure — polished rules governing a position that was never decided. Build the foundation, then earn each stage. → Per-stage entry/exit detail in [`references/corpus-architecture.md`](references/corpus-architecture.md).

## Read-before-write discipline

The corpus is a single source of truth, so writing into it is a careful act:

1. **Read before you overwrite.** Before changing or replacing any corpus file, read the current version. A brand document usually encodes a _decision_ — clobbering it silently discards that decision and the reasoning behind it.
2. **Confirm before you write.** Before adding a new file or overwriting an existing one, confirm the **layer**, the **convention** (flat vs folder), and the **filename** with the user. Wrong layer or mixed convention is a corpus defect that compounds.
3. **Append decisions to 08, don't rewrite history.** When strategy changes, record the change and its reasoning in `08-evaluation`; supersede rather than delete, so the corpus remembers why.
4. **One convention, one source of truth.** Never create a parallel copy "just for now" — two copies of a foundation diverge within a week.

## The brand-corpus MCP (live-data complement)

This skill defines the **static methodology** — the structure files _should_ take. The **`brand-corpus` MCP** is the **live-data complement**: it provides retrieval over a specific brand's actual documents and tokens (search, list, outline, fetch sections, get tokens). Use them together — this skill to decide _where a thing belongs and how it's named_; the MCP to _read what is actually there_ before you write.

When the MCP is available, **query it before structuring** so your corpus reflects reality rather than assumption.

→ **Standing up the MCP** — the language-agnostic tool contract, the canonical `BRAND_CORPUS_DIR` env var (alias `BRAND_CORPUS_ROOT`), choosing a Python vs TS implementation, and the three ways to register it (bundled in a plugin / standalone / published): [`references/mcp-wiring.md`](references/mcp-wiring.md).

## Stamping the corpus into a distributable

A finished corpus is _emitted_ for a host via **`/brand-stamp`** (mechanized by `bin/brand-stamp`), in one of three **pure, separate** forms — each to its own folder: a **plugin** (corpus + the stdio `brand-corpus` MCP, for Claude Code / Cowork), a **cloud skill** (the corpus bundled in a skill's `references/`, for Claude chat — no MCP/scripts), or a **standalone MCP** (the server + corpus + a `claude mcp add` recipe). → [`references/stamping.md`](references/stamping.md).

## Boundaries

- This skill organizes documents; it does not **write** the strategy (`brand-methodology`) or **score** it (`brand-evaluate`).
- → Full layout, per-layer contents, per-stage detail, and naming examples: [`references/corpus-architecture.md`](references/corpus-architecture.md).

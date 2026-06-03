# Corpus Architecture

The full reference for the canonical brand corpus: the eight layers and their contents, the two
output conventions with worked filename examples, the maturity stages with entry/exit criteria,
and the write discipline. The `SKILL.md` is the summary; this is the detail.

---

## The eight layers, in full

The numbering is **load order** — each layer is valid only if the layers above it exist and it
descends from them.

### 01 — Foundation *(load-bearing)*
The strategy everything else stands on. Contents: the cultural root, the position, the point of
view, the enemy/tension, the customer transformation, the editorial principles. This is the
3-page minimum-viable foundation (see `brand-methodology`). **If 01 is missing or undecided, every
layer below it is decoration.**

### 02 — Positioning
The expansion of the position: positioning territories explored and chosen, the category-design
narrative (the frame the brand wants the market to adopt), and competitive archaeology (how rivals
earned — or failed to earn — their meaning).

### 03 — Identity
The visual idea made concrete: the logo system, marks and lockups, and the single visual concept
the identity expresses. Must trace to the POV in 01.

### 04 — Expression
The expression system: type scale and pairings, color strategy, layout and grid, imagery
direction, and motion. This is the kit makers use; every choice should be defensible from 01–03.

### 05 — Voice
How the brand speaks: tone, naming conventions, copy principles (we-write / we-don't), and worked
examples across contexts. Voice is the POV spoken aloud.

### 06 — Product
The brand as *experienced* — in the product, the UX, the actual moments of use. Does using the
thing feel like the brand 01 claims? This layer keeps the brand honest.

### 07 — Guidelines
Governance and the rules of coherence: usage rules, do/don't, decision rights, and enough that a
stranger can extend the brand correctly without asking. Guidelines without 01–06 beneath them are
rules for a brand that does not yet exist.

### 08 — Evaluation
The feedback loop: audits, rubric scores (see `brand-evaluate`), council reviews, and the
**decision log** — what changed, when, and why. Findings here feed back into 01. This is what
turns a brand from a snapshot into something stewarded.

---

## The two conventions — worked examples

Pick one by destination and hold it for the entire corpus.

### Flat (Claude Project knowledge)
No directories exist, so the **double-hyphen prefix `NN-layer--`** carries the layer and preserves
ordering and grouping in a flat namespace:

```
01-foundation--the-position.md
01-foundation--cultural-root.md
01-foundation--editorial-principles.md
02-positioning--territories.md
03-identity--logo-system.md
04-expression--type-and-color.md
05-voice--tone-and-naming.md
07-guidelines--usage-rules.md
08-evaluation--2026-q2-audit.md
```

The single `--` is load-bearing: it splits the *layer* (left) from the *document* (right). The
leading number sorts the whole corpus into load order in any flat file list.

### Folder (filesystem)
Directories are native; the **path is the layer**, so filenames drop the prefix:

```
01-foundation/
  the-position.md
  cultural-root.md
  editorial-principles.md
02-positioning/
  territories.md
03-identity/
  logo-system.md
04-expression/
  type-and-color.md
05-voice/
  tone-and-naming.md
07-guidelines/
  usage-rules.md
08-evaluation/
  2026-q2-audit.md
```

### The never-mix rule
A corpus is **wholly flat or wholly nested**. Mixing breaks retrieval (the MCP and humans expect
one shape) and corrupts the mental model. Migration is mechanical and reversible:
`01-foundation--the-position.md` ⟷ `01-foundation/the-position.md`. If you encounter a mixed
corpus, reconcile to one convention *before* adding anything new.

---

## Maturity stages — entry / exit criteria

| Stage | Enter when… | Exit (→ next) when… |
|---|---|---|
| **0 — Empty** | Nothing structured exists | The 3-page foundation is written |
| **1 — Seed** | 01 foundation exists and is decided | Positioning territories are chosen |
| **2 — Positioned** | 01–02 complete | A visual identity exists |
| **3 — Identified** | 03 identity descends from 01 | A working expression system exists |
| **4 — Expressed** | 01–05 form a usable kit | The brand lives in the product with stranger-followable guidelines |
| **5 — Operational** | 01–07 complete and in use | Audits/reviews begin feeding back into 01 |
| **6 — Stewarded** | 08 closes the loop into 01 | (steady state — maintained, not "finished") |

**The cardinal anti-pattern:** producing a late-stage artifact on an early-stage foundation — e.g.
stage-5 guidelines governing a stage-1 (undecided) position, or a stage-4 expression system with
no stage-3 visual idea. The polish hides the missing decision. Always build down the stack, not
ahead of it.

---

## Write discipline (expanded)

1. **Read before overwrite** — load the current file first; it usually encodes a decision worth
   preserving.
2. **Confirm before write** — confirm layer + convention + filename with the user before creating
   or replacing.
3. **Supersede, don't delete** — when strategy changes, record the change and its reasoning in
   `08-evaluation`; keep history so the corpus remembers *why*.
4. **One source of truth** — never fork a "temporary" parallel copy; copies diverge fast.
5. **Query the MCP first** — when the `brand-corpus` MCP is available, read what actually exists
   before structuring, so the corpus reflects reality, not assumption.

---

## Extension point

A production deployment expands this reference with: a per-layer file manifest (the exact set of
documents each layer expects at maturity), corpus templates for each output convention, a
migration script between flat and folder shapes, and an audit checklist that maps to the
`08-evaluation` rubric scores. All of it descends from the eight layers and two conventions
defined here.

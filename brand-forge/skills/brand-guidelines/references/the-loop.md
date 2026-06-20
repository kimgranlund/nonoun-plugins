# The guided 2×2 elicitation loop — full mechanism

The `SKILL.md` is the summary; this is the detail. The loop **builds a brand-guidelines section by guided choice**, one domain at a time, accumulating typed choices into a ledger the assembler later compiles into the corpus. The discipline: the model proposes concrete options; the designer chooses + corrects; **code owns the state and the assembly** (structure is mechanized, taste is not).

---

## The walk — six domains, the idea above them

The loop walks `mark · voice · color · type · expression · governance` (brand-decomposer's six rubric-aligned domains; `expression` is the wide rollup — layout, photography, illustration, iconography, motion, product-UI, dataviz, social, marketing, packaging, environmental, co-branding). Above all six sits the **brand idea** from `01-foundation`: every option must trace to it, and the loop refuses to elicit a domain whose options can't descend from a decided foundation (the corpus's load-order rule).

Order: `mark → voice → color → type → expression → governance` (governance last — it codifies what the others decided). The designer can jump to any domain; the ledger tracks coverage either way.

## The 2×2 recipe

For a domain, cross **two of the seven axes** into a 2×2:

`functional↔expressive · product-led↔human-led · quiet↔loud · literal↔metaphorical · premium-restraint↔campaign-loudness · institutional↔conversational · systematic↔organic`

**Default axis pair per domain** (a deterministic default for predictability + resumability; the model may swap a pair *with a stated reason*; the designer may override):

| Domain | Default 2×2 | Why this pair |
|---|---|---|
| mark | literal↔metaphorical × systematic↔organic | is the mark a literal depiction or a metaphor; geometric or organic |
| voice | institutional↔conversational × functional↔expressive | register × how much personality the words carry |
| color | functional↔expressive × restraint↔loudness | is color a UI role or a brand signal; how much of it |
| type | systematic↔organic × functional↔expressive | rational/neutral vs. characterful; workhorse vs. voice-carrying |
| expression | quiet↔loud × premium-restraint↔campaign-loudness | the energy + restraint of the whole expression grammar |
| governance | systematic↔organic × product-led↔human-led | how much process; centralized vs. delegated authorship |

Each quadrant becomes one **design-move card**, generated grounded in (a) the brand idea + prior choices, (b) a **cited exemplar** (name the brand + the mechanism, never copy its assets), and (c) the quality bar for that domain. **No generic options** — every card names a causal mechanism; never "modern/bold/clean," never "on-brand."

### The design-move card (what a quadrant renders as)

```
[B] expressive + restrained
A signature accent on a near-neutral base — one hot color used sparingly as the brand's "tell."
  Why: lets the foundation's "quiet confidence" read while still owning one ownable color.
  Effect: recognition at a glance without shouting; contrast headroom for accessibility.
  Like: Stripe — accent on white (restrained-expressive at scale).
```

## The pick model

Present the 2×2 as a Markdown grid + the four lettered cards, then ask for **one quadrant (A/B/C/D) + free-text comments/corrections**. One quadrant is the primary capture (it keeps the ledger unambiguous + the coherence graph clean). A comment may **amend** the chosen move ("B, but warmer — terracotta") or **request a blend** ("B's base with C's energy") — in which case record the **amended move verbatim** *and* **re-render a refined card for confirmation** before appending, so the ledger faithfully reflects intent. (Whether to support a first-class multi-quadrant "blend" pick is an open question; today a blend is captured as an amended single choice.)

## Capture → the choice-ledger

Append a typed **choice** to the ledger (validated by `bin/guidelines-ledger`):

```json
{ "id": "color-r1", "domain": "color", "round": 1,
  "axes": ["functional-expressive", "restraint-loudness"],
  "presented": ["A","B","C","D"], "chosen": "B",
  "comment": "warmer — terracotta not blue",
  "move": { "move": "...", "rationale": "...", "expected_effect": "...",
            "exemplar_evidence": [{"brand":"Stripe","what":"accent on white","why_cited":"restrained-expressive at scale"}],
            "confidence": 0.8 },
  "contributors": [{"who":"designer","role":"chooser","date":"2026-06-20"},
                   {"who":"brand-guidelines","role":"proposer","date":"2026-06-20"}],
  "supersedes": null }
```

**Location:** the ledger lives in the corpus so the assembled docs can `sources:`-cite it — recommended `00-sources/guidelines-elicitation.json` (it is evidence: the choices that produced the guidelines). Append-only; a revision sets `supersedes` to the earlier entry id (never rewrite a decision — the corpus write-discipline). Validate after every write: `guidelines-ledger validate <path>`.

## Drill-down

A domain isn't done at one 2×2. Its **capture spec** (the sub-decisions a complete treatment resolves — for color: roles · meaning · ratios · light/dark · contrast/accessibility · product vs. marketing usage · misuse) is the drill-down map: a chosen quadrant spawns a **finer 2×2** within it (e.g. after B "signature accent": warm↔cool × single↔family). Bounded by the capture spec — when its sub-decisions are resolved (or explicitly deferred), the domain is covered. Earlier (coarser) choices constrain the finer ones.

## Coherence — earlier choices constrain later domains

Choices aren't independent: a loud-expressive color should inform the type + expression options offered next. Each accepted choice can write **coherence edges** into the ledger's `graph` (brand-decomposer's relationship vocabulary — `constrains · supports · contradicts · …`); when framing a later domain's 2×2, read the graph so options stay coherent with prior commitments, and **flag** (don't silently forbid) a candidate that `contradicts` an earlier choice. Coherence *informs*; it doesn't railroad.

## Assembly + scoring (later increment — the loop closes)

When coverage is reached, the **assembler** compiles the ledger → corpus docs deterministically (no inference in the compile): each domain's resolved choices → `04-expression--*.md` / `05-voice--*.md` / `03-identity--*.md` / a `07-guidelines` section, every rule typed `must/should/may` and written as a causal mechanism, each doc carrying `sources:` (the choices + exemplars) + `contributors:` (designer + system) frontmatter. Then `corpus-provenance` gates the trace and **`brand-evaluate`** scores the result. The **brand-decomposer seam**: the assembler can additionally project a `*.brand.json` card for grading + operability-checking by `design-skills:brand-decomposer` when installed (optional; brand-forge stays self-contained).

## Relationship to brand-decomposer (parallel, not a dependency)

We MAKE; brand-decomposer GRADES. We mirror its six domains, seven axes, and evidence discipline as **vocabulary** (restated, not imported — it's a different marketplace and brand-forge is self-contained), and hand it gradeable output via the optional card-projection seam. We do not re-implement its rubric, schema, or operability checker.

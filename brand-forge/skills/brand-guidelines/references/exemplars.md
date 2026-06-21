# Exemplars — option-generation seeds, by domain and axis

When the loop generates the four design-move cards for a domain's 2×2, each card should **cite an exemplar** — a real brand whose public approach demonstrates that quadrant's *mechanism*. This file is the seed library: per-domain exemplars keyed to where they sit on the axes, so a card reads *"like X — which does Y"* rather than a generic option. It sharpens generation; it is not a grading bar (that is `brand-evaluate` and `design-skills:brand-decomposer`).

## The citation discipline (read first)

- **Cite the mechanism, never the asset.** Name the brand and describe *what it does* and *why it works* — "a restrained neutral system with one signature accent." Do **not** reproduce its logo, palette hex, type, or guidelines. Public, observable approach only; fair commentary, not asset redistribution.
- **Link-only for anything deeper.** If you point at a brand's actual guidelines, link to the public source; never bundle or paraphrase it wholesale.
- **An exemplar is evidence the move is *possible*, not a license to copy it.** The chosen move must still descend from *this* brand's `01-foundation`. An exemplar that doesn't trace to the foundation is decoration — drop it.
- **This is a seed list, not the catalog.** For a deep, annotated reference-deck set, `design-skills:brand-decomposer` carries the curated catalog (link-only). Cite from real knowledge of the brand; if unsure of a brand's actual approach, say so rather than invent it.

## Per-domain exemplar seeds (by axis position)

Illustrative, not exhaustive — pick the one whose *mechanism* fits the card, and name that mechanism.

### mark *(literal↔metaphorical × systematic↔organic)*
- **Literal + systematic** — a geometric monogram or initial built on a grid (legible at a favicon, trademark-clean).
- **Metaphorical + systematic** — an abstract symbol encoding the idea in a constructed form (the "tells a story but holds up small" mark).
- **Metaphorical + organic** — a hand-drawn or gestural mark that signals craft/humanity over system.
- *Cite the construction logic + what the symbol means, not the glyph.*

### voice *(institutional↔conversational × functional↔expressive)*
- **Institutional + functional** — spare, authoritative, outcome-first; gravitas through restraint.
- **Conversational + expressive** — warm, direct, personality-forward; a brand that "talks like a person."
- *Cite the writing behavior ("leads with the outcome, cuts the hedge"), never adjectives.*

### color *(functional↔expressive × restraint↔loudness)*
- **Functional + restrained** — a tight semantic palette, color as UI role (status/hierarchy), near-neutral base.
- **Expressive + restrained** — a neutral system with **one** signature accent used sparingly as the brand's "tell."
- **Expressive + loud** — a brand that *is* its color (saturated, ownable, campaign-forward).
- *Cite the role + ratio mechanism ("one hot accent on neutral, ~5% coverage"), not hex.*

### type *(systematic↔organic × functional↔expressive)*
- **Systematic + functional** — a neutral workhorse + a clear modular scale; type as quiet infrastructure.
- **Organic + expressive** — a characterful display face carrying the voice; type as the signature.
- *Cite the rationale ("the display face *is* the wordmark's relative") + the hierarchy, not the font name alone.*

### expression *(quiet↔loud × premium-restraint↔campaign-loudness)*
- **Quiet + premium** — generous whitespace, restrained imagery, product-true photography; "the room is expensive."
- **Loud + campaign** — high-energy layout, bold type, saturated imagery; the expression grammar shouts the idea.
- *Cite the grammar (grid logic, imagery rule, motion principle) that lets new work be generated, not copied.*

### governance *(systematic↔organic × product-led↔human-led)*
- **Systematic + product-led** — versioned tokens, an owned component library, approval gates; the brand as an operated system.
- **Organic + human-led** — lightweight principles + a named steward; coherence by judgment over policy.
- *Cite the change process + decision rights, the part that decides whether the system survives contact with a real org.*

## Using this in the loop

Per card: pick the exemplar whose quadrant matches, state the mechanism (`Like X — which does Y`), and check it traces to `01-foundation`. The exemplar goes into the choice's `move.exemplar_evidence` (brand · what · why_cited), so the assembled rule and the projected brand-spec card both carry the citation.

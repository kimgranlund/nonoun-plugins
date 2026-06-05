---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jesse G., *The Elements of User Experience: User-Centered Design for the Web* (New Riders, 1st ed. 2002; 2nd ed. 2010)."
  - "Jesse G., *The Elements of User Experience* diagram / chapter excerpts (jjg.net/elements)."
---

# The Five Planes (Jesse G.)

This is the working method for using Jesse G.'s five planes as the structural spine of an experience architecture — not as a summary of the book, but as a procedure for laying out a product so that every layer rests on the one beneath it. Jesse G.'s framework decomposes user experience into five planes stacked from abstract to concrete: **strategy → scope → structure → skeleton → surface**, built bottom-up. Its single load-bearing claim is the dependency rule: **the surface depends on the skeleton, which depends on the structure, which depends on the scope, which depends on the strategy.** Each plane is a chance to solve a different problem, and a decision on a higher plane is only as sound as the plane below it. Get the order wrong — pick a navigation pattern before you know the strategy — and you are decorating a foundation that may not hold.

## The five planes, bottom to top

Read them from the ground up, because that is the order in which they get decided. Each plane answers one question and hands a constraint to the next.

| Plane | Abstraction | The question it answers | The artifacts it produces |
| --- | --- | --- | --- |
| **Strategy** | Most abstract | What do we want from the product (business objectives), and what do users want from it (user needs)? | Product objectives, user needs, success metrics |
| **Scope** | ↓ | Given the strategy, what must the product _do_ and _contain_? | Functional specifications + content requirements |
| **Structure** | ↓ | How are the pieces organized and connected; how does the system behave as the user moves through it? | Interaction design + information architecture |
| **Skeleton** | ↓ | Where do the components sit on each screen, and how do they arrange the structure for use? | Interface design, navigation design, information design (wireframes) |
| **Surface** | Most concrete | What does the user actually see, hear, and touch? | Sensory/visual design — the final composition |

The plane names are deliberately not "phases." Work overlaps in time; the dependency is logical, not strictly sequential. But the constraint always flows the same direction: lower planes bound higher ones.

## The dual nature (Jesse G.'s two-axis grid)

Jesse G.'s diagram is not a single column — it is split vertically into **two halves** that run up through every plane, because a product is simultaneously two things: a **software interface** (a tool you use to get tasks done) and a **hypertext / information system** (a body of content you move through). Most real products are a blend, and the split tells you which discipline owns each plane.

```text
                 SOFTWARE-INTERFACE side        HYPERTEXT / INFORMATION side
                 (the product as a TOOL)        (the product as CONTENT)
   ─────────────┬──────────────────────────────┬──────────────────────────────
   SURFACE      │            visual / sensory design (one surface)            │
   ─────────────┼──────────────────────────────┼──────────────────────────────
   SKELETON     │   interface design           │   navigation design          │
                │        └────────── information design ──────────┘           │
   ─────────────┼──────────────────────────────┼──────────────────────────────
   STRUCTURE    │   interaction design         │   information architecture    │
   ─────────────┼──────────────────────────────┼──────────────────────────────
   SCOPE        │   functional specifications  │   content requirements        │
   ─────────────┼──────────────────────────────┼──────────────────────────────
   STRATEGY     │   product objectives  ·  user needs  (shared foundation)    │
   ─────────────┴──────────────────────────────┴──────────────────────────────
```

The practical payoff: when you hit a plane, you immediately know which two questions to ask. On scope, "what features?" (functional) _and_ "what content?" (informational). On structure, "what's the interaction model?" (interaction design) _and_ "how is content categorized and linked?" (information architecture — see `navigation-and-wayfinding.md`). A product that is mostly a tool leans left; a product that is mostly content leans right; ignoring the side your product actually lives on is a common source of mismatched effort.

## Using the planes as an architecture spine

Treat the stack as a checklist you walk bottom-up before committing to any visible design. The discipline is to refuse to answer a higher plane until the one below is resolved.

1. **Strategy first, and write it down.** Jesse G. is explicit that "the most common reason for the failure of websites is not technology. It's not user experience either. The most common reason… is the lack of a clearly articulated strategy." Name the product objectives (what the business gets) and the user needs (what users get) — separately, so you can see where they conflict. This plane is the same territory the product-strategy references cover; the planes inherit a strategy, they don't manufacture one.
2. **Derive scope from strategy, not from a wish list.** A feature earns a place in scope only if it serves a stated objective or need. Jesse G.'s value in writing scope down is twofold: it forces you to decide what you're building, and it forces you to decide what you're _not_ building. A scope plane that contains everything anyone asked for has skipped the derivation.
3. **Turn scope into structure.** Now — and only now — decide the interaction model (how the tool responds to the user) and the information architecture (how content is organized and connected). This is where flows (`flows-and-task-design.md`) and IA take shape.
4. **Lay the structure onto a skeleton.** Wireframe placement: where navigation, content, and controls sit on each screen. The skeleton makes the abstract structure usable; it is the level of "what goes where," not "what color."
5. **Apply the surface last.** Visual and sensory design composes the skeleton into the thing the user perceives. Surface decisions cannot fix a broken structure — they can only present whatever structure exists.

## The tell of good vs. bad

The signature of a well-architected product is that you can trace any surface element down through the planes to a strategic reason for its existence. The signature of a badly architected one is an orphan — a screen, a tab, a feature that exists for no reason traceable below the surface.

- **Good:** "This nav item exists because the structure groups these tasks; that grouping exists because scope included this feature set; that feature set exists because the strategy named this user need." Every layer cites the one below.
- **Bad — top-down contamination:** the visual design (surface) was chosen first, and scope/structure were back-filled to fit it. Symptom: features that exist "because the mockup had space," navigation that mirrors the org chart rather than the content.
- **Bad — skipped plane:** jumping from strategy straight to surface (a beautiful comp with no IA underneath), or from scope straight to skeleton (wireframes with no interaction model). The missing plane shows up later as rework when the gap surfaces.
- **Bad — strategy as decoration:** a "strategy" that is a vision statement with no product objectives or user needs the rest of the planes can be derived from. Then scope has nothing to be accountable to, and feature creep is unbounded.

## What to check (a plane audit)

When reviewing an experience architecture against this spine, ask in order:

- **Strategy present and bifurcated?** Are business objectives and user needs both stated, and are the points where they conflict acknowledged rather than hidden?
- **Scope traceable?** Does every feature/content requirement map up to a strategic line? Is there an explicit list of what was cut?
- **Structure before skeleton?** Is there an articulated interaction model and IA, or do wireframes exist with no documented structure behind them?
- **Right side of the dual axis?** Is effort going to the tool side or the content side in proportion to what the product actually is?
- **Dependencies flowing upward only?** Look for any decision on a lower plane that was made to accommodate a higher one (a structure bent to fit a chosen visual, a scope expanded to fill a layout). That inversion is the defect the framework exists to catch.

## One labeled caveat

The plane names, the bottom-up dependency rule, and the dual-nature (software-interface vs. hypertext) split are unambiguous and consistent across Jesse G.'s book, his published diagram, and every secondary summary. The exact wording quoted here ("The most common reason… is the lack of a clearly articulated strategy") is attributed to _The Elements of User Experience_ and cross-checked against widely reproduced excerpts rather than against a page-numbered print edition in this session; confirm verbatim wording and edition (2002 vs. 2010) against the print copy before quoting for publication. Note also that the second edition broadened the framing from "the Web" to user-centered product design generally — the planes are identical, only the examples differ.

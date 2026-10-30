# Best practices — intent grilling

> How to derive the load-bearing design decisions from two axes and grill them out across cascading
> rounds, until the surface is settled enough to decompose. 2026-06-28. (Mental models: `foundations.md`.)

## Do

- **Frame the space before you ask.** Name what's being designed and sketch **both** axes — Structural
  (scope · consumer · element set · composition · sequencing) and Mechanism (primitives · capabilities ·
  geometry/semantics · fidelity) — *before* writing a single question.
- **Derive from both planes every round.** Pull forks from Structural **and** Mechanism; a round drawn
  from one plane only inherits that plane's blindness (a scope with no idea what's hard to build, or
  clever primitives with no agreed shape).
- **Rank by cascade reach, not by how unsure you feel.** Ask the fork whose answer most reshapes the
  *rest* of the design. Round 1 = the 2 highest-leverage Structural + 2 Mechanism forks.
- **Ground every option in the codebase first.** Inspect the catalog / tokens / constraints so each
  option is concrete ("align to the reserved `Row`/`Column`/`Card` names"), with a recommendation + its
  tradeoff. An abstract option gets rubber-stamped; a grounded one gets decided.
- **Let each answer reshape the next round.** Re-derive the surface after every round — a "full set"
  scope pulls in the stateful-composite + sequencing forks; a chosen mechanism closes some forks and
  opens others. The cascade *is* the method.
- **Synthesize across both planes.** End on a Ratified Design that names decisions on Structural **and**
  Mechanism, ready to hand to `decompose` / docs' `the document author` (`the doc rules`).

## Don't

- **Run one axis.** Structural-only or Mechanism-only is a single-plane decomposition — self-confirming
  and blind to the other's failure.
- **Ask an abstract fork.** "Flexible vs simple?" with no concrete options is a non-decision; ground it
  in real catalog/token/constraint facts first.
- **Pre-plan all the rounds as a flat checklist.** If round 3 was written before round 1 was answered,
  the answers didn't reshape anything — you ran a questionnaire, not a grilling.
- **Over-grill.** Manufacturing rounds past convergence is the proactive mirror of over-clarifying; it
  spends the author's attention for no change in the design. Converge on a *settled surface*, not the
  absence of every small doubt.
- **Stop short.** Leaving a load-bearing (cascading) fork to a silent default ships an unhosted decision
  to `decompose` — caught only downstream, expensively.
- **Drip.** Multiple rounds are not dripping — each round is a full batch. Never trickle one question per
  turn.

## Techniques worth stealing

- **The cascade map.** After each round, write the one-line consequence of each answer ("full set →
  pulls in Tabs/Modal a11y + composition"). The map *is* the next round's surface; it also proves the
  rounds weren't pre-planned.
- **Ground-then-reframe.** Investigate before round N+1 specifically to *reframe* a fork — the
  container-family session inspected the catalog, discovered `Row`/`Column`/`Card` were reserved, and
  reframed the element-set question around the reserved names rather than free invention.
- **Tag every decision `[S]`/`[M]`.** Carrying the axis tag through to the Ratified Design makes the
  both-planes check trivial: a design with no `[M]` decisions (or no `[S]`) failed to grill one plane.
- **Recommend-with-tradeoff.** Lead every option set with "(recommended) … — tradeoff: …". The author
  decides by *editing* a recommendation faster than by composing from scratch (shared with
  `clarify`'s closed-question discipline).

## The validation loop

Before handing off, check the Ratified Design and fix until clean: **both-planes** (decisions on
Structural *and* Mechanism?), **leverage** (each round the highest-cascade forks, none silently
defaulted?), **grounding** (every option concrete, traceable to a codebase fact?), **convergence**
(stopped at settled — no over-grilling, no unhosted load-bearing fork?), **handoff** (could
`decompose` run both planes without re-grilling?).

---

Sources: [Design space exploration](https://en.wikipedia.org/wiki/Design_space_exploration) ·
[Architecture Decision Records](https://adr.github.io/) ·
[Rolling-wave / progressive elaboration (PMI)](https://www.pmi.org/learning/library/rolling-wave-planning-progressive-elaboration-6822) ·
companion: `.claude/skills/clarify/`

# Foundations — intent grilling

> The load-bearing models behind *deriving* the decisions a greenfield implies, before it can be
> decomposed. Grounded in design-space exploration, decision analysis, and progressive planning
> (sources at the foot). 2026-06-28.

## Reactive vs proactive elicitation

`clarify` is **reactive**: a request already exists; you recover the goal under its words and
resolve only the gaps that change the output. **Intent grilling is proactive**: little has been asked
yet, but a design *must* be settled. You cannot wait for an ambiguous ask to react to — you **derive**
the decisions the thing-being-designed implies. Reactive elicitation minimizes questions; proactive
derivation enumerates the decision space and then prioritizes within it.

## The design space and its load-bearing decisions

A design problem opens a **design space** — the set of all candidate designs, spanned by the decisions
that are still free. Most of those decisions are low-leverage (they don't constrain the others). A few
are **load-bearing**: their answer *cascades*, fixing or foreclosing many downstream choices. The whole
job is to find and settle the load-bearing decisions in leverage order, so the rest fall out cheaply.
This is design-space *exploration* applied at intake — and an **Architecture Decision Record** is the
durable form of exactly such a decision.

## Two planes, applied to question derivation

The two crossing planes of `decompose` — **OUTSIDE-IN** (whole → parts, structure) and
**INSIDE-OUT** (atoms → surfaces, behavior) — are not only a way to break down a *known* design; run
*before* the design exists, they are a way to **derive the questions**. Structural forks come from the
outside-in plane (scope, consumer, element set, composition, sequencing); Mechanism forks from the
inside-out plane (primitives, capabilities, geometry/semantics, fidelity). A single plane is
self-confirming and blind to the other's failure — the same reason `decompose` insists on
both. Crossing them is what makes the load-bearing forks visible.

## Decision leverage = value of information

Which fork to ask first is a **value-of-information** question: the fork worth asking is the one whose
answer most reduces the uncertainty in the *rest* of the design. A high-leverage fork cascades; a
low-leverage one is defaultable in isolation. Rank by cascade reach, not by how unsure you happen to
feel — feeling-unsure is the wrong meter (it is also the over-asking trap that sinks extraction).

## Cascading rounds = progressive elaboration

You cannot pre-plan round 3 before round 1 is answered, because the answers **reshape the surface** — a
"full set" scope pulls the stateful-composite and sequencing forks into existence; a chosen mechanism
closes some forks and opens others. This is **progressive elaboration / rolling-wave planning**: detail
the near rounds, leave the far ones coarse, and let each answer reshape what comes next. It is the
single, principled exception to extraction's "never drip" rule — each round is still a full batch; you
add a round only because the surface genuinely changed.

## Ground options or get a rubber-stamp

An **abstract** option ("a flexible layout system") carries no information for the author to decide on,
so it gets rubber-stamped — the decision is deferred under the appearance of being made. A **concrete**,
codebase-grounded option ("align to the reserved `Row`/`Column`/`Card` catalog names") anchors a real
choice. Grounding the option set in the actual catalog/tokens/constraints *before* asking is what turns
a question into a decision. This is **set-based** thinking: investigate the real feasible set, then
commit the load-bearing decision — don't ask the author to commit to a fiction.

## Convergence and the over-grilling failure

Stop when every remaining fork is defaultable-without-cascading or downstream of a decision
`decompose` will make anyway. Past that point, more rounds are **over-grilling** — the
proactive mirror of extraction's over-clarifying. Both spend the author's attention for no change in the
output. Convergence is a settled *surface*, not an absence of every small doubt.

---

Sources: [Design space exploration](https://en.wikipedia.org/wiki/Design_space_exploration) ·
[Architecture Decision Records](https://adr.github.io/) ·
[Value of information](https://en.wikipedia.org/wiki/Value_of_information) ·
[Rolling-wave / progressive elaboration (PMI)](https://www.pmi.org/learning/library/rolling-wave-planning-progressive-elaboration-6822) ·
[Set-based design (SEBoK)](https://sebokwiki.org/wiki/Set-Based_Design)

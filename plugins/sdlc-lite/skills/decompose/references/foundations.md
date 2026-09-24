# Foundations — decomposition (the two-plane method)

> The load-bearing models the method rests on. The **procedure** depth is `method.md`; the **domain**
> vocab is `references/<domain>.md`; this file grounds *why* the method is shaped as it is, in
> established practice (sources at the foot). 2026-06-26.

## Decomposition is the oldest design move

**Functional decomposition** (a.k.a. top-down design / functional analysis / logical decomposition)
divides a whole into smaller sub-tasks, recursively, until each is directly buildable. Its governing
law: **the children must completely describe the parent** — a breakdown that omits part of the parent,
or adds what isn't in it, is wrong. That is the completeness half of **MECE** (mutually exclusive,
collectively exhaustive).

## Two directions, two blindnesses

- **Top-down (OUTSIDE-IN)** starts from the whole and refines into parts — a tidy structure whose leaves
  are never tested against real needs.
- **Bottom-up (INSIDE-OUT)** starts from irreducible units and composes upward — real needs never forced
  into a coherent whole.

Each direction is self-confirming and blind to the other's failure. Conventional decomposition runs
**one** direction; this skill runs both so the blindness becomes a visible gap.

## The cross-check is the correctness unit

Soundness is not "a clean tree" — it is that the two **independently-derived** planes cover each other.
The defect quadrant (`method.md`): an **unhosted action** (a need with no surface) or an **unjustified
leaf** (structure with no need) are the two silent failures a single plane ships. Independence is the
trick — if the action set is read off the node tree, you have run one plane twice and learned nothing.

## MECE — the two failure axes

- **Collectively exhaustive** — every part of the parent is covered (no gap). An unhosted action is an
  exhaustiveness failure of the *structure*.
- **Mutually exclusive** — parts don't overlap (no double-owned responsibility). Overlap manufactures
  coordination cost.

## Granularity is a decision

Stop dividing at **one responsibility, one owner, one contract** — directly buildable/assignable. Both
*under*-decomposition (a "leaf" still hiding a seam) and *over*-decomposition (splitting past a single
owner) are defects; the second manufactures coordination cost. Each domain reference states the concrete
stop rule.

## Decompose before authoring

A cleared decomposition is the **input** to authoring, not its output: OUTSIDE-IN structure →
SPEC/LLD components; INSIDE-OUT actions → acceptance criteria / tests. Decompose first, then author
against the result.

---

Sources: [Functional decomposition (PSU ME491)](http://web.cecs.pdx.edu/~gerry/class/ME491/notes/functional_decomposition.html) ·
[Work Breakdown Structure principles (PMI)](https://www.pmi.org/learning/library/work-breakdown-structure-basic-principles-4883) ·
[Top-down design](https://www.cs.usfca.edu/~parrt/course/601/lectures/top.down.design.html)

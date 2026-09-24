# The two-plane method (depth)

> Reference for `decompose`. The SKILL.md owns the one-screen summary; this file owns the method depth. · 2026-06-26

## Why two planes

A single-direction breakdown is self-confirming: top-down produces a tidy tree whose leaves you never test against real needs; bottom-up produces a pile of needs you never force into a coherent whole. Each direction is blind to the other's failure. Running both and crossing them turns the blindness into a visible gap.

## OUTSIDE-IN (structure)

Start from the whole in its context and divide, top-down. At each level ask: *what are the parts here, and how do they nest?* Produce a **node tree**. Keep dividing a node until the **stop rule** fires. Tag a node `leaf` when it stops dividing; tag a pure-structure node (one that exists to group, space, or afford rather than to host a need) with a `justify`.

## INSIDE-OUT (behavior / needs)

Independently — do not read the node tree while doing this, or it biases you — enumerate the irreducible units the thing must serve: the verbs, needs, capabilities, or atoms. Compose upward: atom → binding (what state/data it touches) → surface (where it must appear) → coherence (how the surfaces hang together). Produce an **action set**.

**Independence is the whole trick.** The two planes are useful only because they were derived separately and can therefore contradict each other. If you grow the action set by reading off the node tree, you have run one plane twice and learned nothing.

## The crossing (the unit of correctness)

Map each action to the node(s) that host it, then read the defect quadrant:

- **UNHOSTED action** — a need with no surface. The structure is incomplete; add or reshape a node.
- **UNJUSTIFIED leaf** — a leaf that hosts no action and declares no reason. Decoration / gold-plating; host a need on it, justify it, or delete it.
- **load-bearing** (action ↔ node) and **declared structure** (justified, action-free) are the two valid states.

This is what `scripts/coverage_check.py` checks. Run it; do not eyeball the map.

## The stop rule (general)

Stop dividing a node, or stop reducing an action, when it is **one responsibility with one owner and no hidden seam** — i.e. directly buildable or assignable without another branch, and mappable to exactly one contract. When the decomposition feeds execution, add the independence test: the unit is **executable from its enumerated inputs alone** — a part that must peek at a sibling's work mid-build is mis-cut, and the fix is a re-cut or an explicit edge, not a leaked context. Over-decomposition (splitting past the point of a single owner) is its own defect: it manufactures coordination cost. Each domain reference states its concrete stop rule.

## Hand-off

The cleared decomposition (node tree + action map, exit-0 manifest) is the input to authoring, not the output of the work. It feeds the spec family directly: OUTSIDE-IN structure → SPEC requirements / LLD components; INSIDE-OUT actions → acceptance criteria / tests. Decompose first, then author against the result.

A handed-off manifest is a versioned contract: when reality forces a replan, write `manifest-v(n+1)` with the diff and the reason rather than mutating the finalized file — downstream work was dispatched against v(n), and an unreconstructable plan history breaks credit assignment when a build fails.

## Picking a domain

Choose the `references/<domain>.md` whose vocabulary fits the thing being decomposed (`layout`, `components`, `technical-architecture`, `ux-architecture`, `goals`). The planes are universal; only their axis vocabulary and stop rule specialize. No fit → copy `_template.md`.

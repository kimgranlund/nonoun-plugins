# Specification Layer — What Counts as Done

`Cell: ontology.fleet.layer-spec · Status: defined · Register: established lineage (DbC, GORE); intent framing is synthesis`

## Specification Layer Definition

A specification is constitutive and teleological knowledge: it defines what counts as
*done* for a unit of work. The spec is intent's canonical residence — intent after
capture and typing. Per-engagement intent becomes a spec; standing intent becomes
policy (see boundary below).

A spec contains: the target state, acceptance criteria expressed as checkable
predicates, preconditions and postconditions, invariants, and explicit non-goals.
Acceptance criteria that cannot be checked mechanically or by a calibrated reviewer
are not criteria; they are hopes.

## Intent and the Specification Layer

Intent is the working fluid of the whole system, not a layer. Its lifecycle: a
principal's want → an utterance → a spec → a plan → execution → output. Each hop is
lossy and loss is multiplicative (fidelity *f* per hop over *n* hops yields *fⁿ*
end-to-end), which is the mechanical reason fuzzy intent at the top is the dominant
root cause of downstream failure. The spec is the hop where intent becomes typed and
checkable.

Specs carry commitment inertia (Bratman's established distinction: an intention is a
commitment that constrains future deliberation, not a mere desire). A validated spec
changes only through the `regenerating` transition — deliberate and ledgered — never
by silent edit. Living is not the same as unstable.

## Specification Decomposition Across Scopes

Intent exists at every scope rung: fleet mission → system product intent →
workflow job-to-be-done → task acceptance criteria → call prompt. Decomposition
soundness: satisfying the child specs must entail satisfying the parent spec.
Established lineage: goal-oriented requirements engineering (KAOS, i*) and HTN goal
refinement. Most intent loss occurs at decomposition boundaries; typed specs at every
rung make the loss measurable instead of discoverable-at-the-end.

## Specification vs Rubric Boundary

The spec is constitutive — it defines what done *is*. The rubric is comparative — it
measures how well. A rubric without a spec scores against vibes. The spec strictly
precedes the rubric in the layer partial order.

## Specification vs Policy Boundary

A spec is intent for this engagement; a policy is intent that holds across all
engagements. Keeping them separate prevents specs bloated with restated inviolables
and inviolables silently renegotiated task by task.

## Specification Artifact Forms

JSON Schema and TypeSpec contracts; intent schemas; acceptance-criteria lists bound to
executable checks; OpenAPI/interface contracts; feature lists with per-item pass
predicates. Design-by-Contract is the established ancestor: preconditions,
postconditions, invariants.

## Specification Validation Signal

A spec cell is `validated` when: its acceptance criteria are executable or bound to a
calibrated review rubric; a rubric cell binds to it without reinterpretation; and its
decomposition (if any) has been checked for entailment. The signal artifact records
all three.

## Specification Failure Modes

Rubric-without-spec (evaluation against vibes). Thrashing specs (no commitment
semantics; replanning every turn). Stale specs (drift — the spec describes a target
nobody holds anymore; worse than no spec because it is trusted). Prose-only criteria
(uncheckable; the loop cannot converge on them). Goals smuggled into methodology
(the *how* dictating the *what*).

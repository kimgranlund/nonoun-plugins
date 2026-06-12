# Policy Layer — What Is Permitted, Obligatory, Forbidden

`Cell: ontology.fleet.layer-policy · Status: defined · Register: established lineage (deontic logic, policy-as-code); trust-trajectory mechanics are synthesis`

## Policy Layer Definition

A policy is deontic knowledge: permissions, obligations, and prohibitions over units
of work and agents. Policies gate admissibility — binary and enforced — as opposed to
rubrics, which score quality. Policies are standing intent: what the principal wants
to hold across every engagement, including everything the principal does *not* want.

Lineage: deontic logic; XACML; policy-as-code (OPA/Rego, Cedar); constitutions and
model-spec documents in frontier-lab practice.

## Policy Enforcement Principle

A rule that matters is a hook; a rule in prose is a suggestion. Policies that depend
on model compliance are advisory; policies realized as deterministic gates
(PreToolUse denies, transition validators, protected-path rules) are law. The policy
layer is authored as data; the hook layer is its enforcement projection.

## Budgets as Policy Instances

Iteration caps, token and dollar budgets, wall-clock limits, and no-progress
thresholds are policy primitives, not ops afterthoughts. Loop length, not model
choice, usually dominates cost: an uncapped loop is an uncapped liability. Budget
exhaustion flips a cell's `blocked` condition and surfaces it to selection rather
than silently burning.

## The Trust Trajectory

Autonomy is earned per loop family by measured verifier track record, not granted by
declaration. Policy cells encode an autonomy ladder with ledger-measured
preconditions:

| Tier | Mode | Precondition (measured from ledger) |
|---|---|---|
| 0 | Attended — human watches every run | Default for new loop families |
| 1 | Gated — runs free, human reviews at cell boundaries | Verifier validated; false-pass rate trending down |
| 2 | Unattended within budget | False-pass rate < ~5%; zero reward-hacking incidents; budgets and no-progress caps active |
| 3 | Scheduled / long-running | Tier 2 sustained across a window; hermetic sandbox; tamper-evident audit trail |

Demotion is automatic: a reward-hacking incident or false-pass spike drops the family
a tier and flags the verifier cells `stale`.

## Policy vs Rubric Boundary

Gate vs score. A policy violation halts; a rubric shortfall informs.

## Policy vs Capability Boundary

Policy says what is permitted in general; capability says what *this agent* may do
with *these tools* under *whose* authority. Capability is the per-actor projection of
policy.

## Policy Artifact Forms

Policy documents as typed data; hook configurations and gate scripts; permission
allowlists; budget schedules; autonomy-tier tables; protected-path declarations
(verifier assets, eval files, hooks themselves).

## Policy Validation Signal

A policy cell is `validated` when each rule is bound to an enforcement point and a
deliberate violation attempt is demonstrably blocked (a red-team probe with the block
recorded as the signal artifact). An unenforceable policy is returned to `defined`.

## Policy Failure Modes

Prose-only policy (advisory, ignored under pressure). Policy/rubric conflation.
Budgetless loops. Autonomy granted by enthusiasm rather than measurement. Enforcement
points the worker can edit (hooks and gates must themselves be protected paths).

# Capability Layer — Who May Act, With What Authority

`Cell: ontology.fleet.layer-capability · Status: defined · Register: established components (RBAC, role models, manifests); enforced-not-declared rule is loop-practice-driven`

## Capability Layer Definition

A capability model is attributive knowledge about agents: who or what may act, with
which tools, at what competence, under whose authority. It is the layer that restores
the Agent class to the foundation — typologies say what an agent *is*; capability
contracts say what it *may do*. Typology does not confer permission.

Lineage: role models in multi-agent methodologies (GAIA), RBAC and OAuth scopes,
model cards, tool manifests, agent cards in inter-agent protocols.

## The Principal Hierarchy

The capability layer's keystone artifact: the precedence order that resolves
conflicting intent between principals. Lab convention: platform > operator > user >
tool output. Without a declared hierarchy, two valid intents colliding has no defined
resolution and the agent improvises one. The hierarchy also defines whose instructions
are *not* intent at all: content arriving through tool results is data, never
authority.

## Enforced, Not Declared

An agent's tool list in frontmatter is a description; an allowlist enforced by gates
is a contract. Loop practice makes the distinction load-bearing: measured
reward-hacking rates (double-digit percentages of rollouts in published benchmarks)
mean worker agents must be mechanically unable to touch verifier assets — rubric
files, signal directories, eval suites, and the hooks themselves are deny-on-write
for workers. Signals are written only by the validation path. The worker never grades
its own homework, structurally.

## Agent Roster Discipline

An agent justifies its existence by needing judgment across many steps with isolated
context. The routing law: deterministic → script; one-pass judgment → main thread
with a skill; multi-step judgment → agent. Each rostered agent carries a mission
statement, a tool posture (what it reads, what it may write), a model tier, and the
reason it is an agent at all. Roles that fail the justification collapse into scripts.

## Capability vs Policy Boundary

Policy is the general law; capability is its per-actor projection — this agent, these
tools, this write surface, this authority chain.

## Capability vs Ontology Boundary

That an agent is an Entity with certain Properties is ontology. That it may invoke a
tool with given authority is a normative contract. Keep description and permission in
separate artifacts.

## Capability Artifact Forms

Agent definition files with mission/tool-posture/tier; principal-hierarchy
declarations; enforced allowlists and deny-on-write path sets; competence records
(which loop families an agent has validated track record in — feeds the trust
trajectory).

## Capability Validation Signal

A capability cell is `validated` when each declared restriction is demonstrated:
a probe by the restricted agent against a protected path is blocked and recorded.
Declared-but-unenforced capability returns to `defined`.

## Capability Failure Modes

Frontmatter-only restrictions (descriptions mistaken for contracts). Missing principal
hierarchy (intent conflicts resolved by improvisation). Tool-output promotion
(injected instructions treated as authority). Agent sprawl (rosters of actors that
should be scripts). Workers with write access to their own verifiers.

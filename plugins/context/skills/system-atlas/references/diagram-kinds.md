# Diagram kinds

Pick from this table, not from taste. The concept's shape decides the diagram type.

| Concept shape | Diagram type | Why |
|---|---|---|
| Lifecycle: one thing moving between states | `stateDiagram-v2` | transitions are the content |
| Handoffs: several parties exchanging messages in order | `sequenceDiagram` | time is the content |
| Gates: a path with refusals and loops | `flowchart LR` | branching is the content |
| One-door adapter: many callers, one door, many backends | `flowchart LR` drawn as a hub | fan-in to fan-out is the content |
| Ownership: who holds what | `flowchart TB` with subgraphs | the boundary is the content |
| Journey: an actor from goal to outcome | `flowchart LR` | steps and failure exits are the content |

## Tiny examples

Lifecycle:

```
stateDiagram-v2
  direction LR
  [*] --> Draft
  Draft --> Review: submitted
  Review --> Draft: changes asked
  Review --> Live: approved
```

Handoffs:

```
sequenceDiagram
  participant W as Worker
  participant G as Grader
  W->>G: handoff path
  G-->>W: 🟢 or 🔴 verdict
```

Gates:

```
flowchart LR
  A["change"] --> G{"check: does it pass?"}
  G -- "no" --> R["🔴 refused"]
  G -- "yes" --> M["merged"]
```

Hub:

```
flowchart LR
  C["caller"] --> D{{"cmd: the one door"}}
  D --> B1[("backend a")]
  D -.-> B2[("backend b, planned")]
```

Ownership:

```
flowchart TB
  subgraph OWN["owner"]
    N["agent: the component"]
  end
  N --> X[("kb: the record it writes")]
```

## Shapes per machinery kind

One shape and one mono prefix per kind. Color never distinguishes a kind.

| Kind | Mermaid shape | Written as |
|---|---|---|
| Skill | rounded | `S("skill: name")` |
| Agent | box inside an ownership subgraph | `A["agent: name"]` inside `subgraph` |
| Command, external door | hexagon | `D{{"cmd: verb"}}` |
| Hook, checker, evaluator, verifier | diamond | `G{"check: what fails"}` |
| Knowledge base, store, config, generator | cylinder | `K[("kb: path")]` |
| Rule | note | `note right of X` in a state diagram, or a labeled node marked `rule:` attached to what it constrains |
| Actor, start, outcome | stadium | `H(["Human"])` |

Decisions are the only accent-colored shape and notes the only warm hue; both come from the
diagram token tier, not from anything written in the diagram source.

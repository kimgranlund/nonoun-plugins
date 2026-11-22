# Recipe: a system's structure

Read before step 3 of the procedure when the question is how parts of a system are arranged: where something
lives, what talks to what, what is built or bought.

| | |
|---|---|
| Specimen | A diagram of the structure with the fixture traced through it step by step: each hop numbered, with what it reads, writes and waits for. The trace is the specimen; a diagram alone is a description. |
| Fixture | One real request, change or failure, the same for every variant, chosen because it is the hard one (the write that must not be lost, the change that touches every part, the slowest path). |
| Stress | A set of named scenarios as a button group marked `data-fb-control-group`: ten times the load, one part down, a new requirement, half the team. Each variant is redrawn or restated for each scenario, and the page says which hop gives out. |

## Choosing variants

The usual axes: where state lives, what is synchronous and what is not, who owns a boundary, what is bought and
what is built, one unit or several. A variant that only renames boxes of another is not a variant.

## Rules for the specimens

- Draw every variant with the same marks: one shape for a store, one for a process, one for a boundary, one kind
  of arrow for a call and another for a message. The reader compares structures, not drawing styles.
- Each variant carries Depends on, and every figure (latency, cost, effort) is marked measured, sourced, estimated
  or assumed.
- Where a variant can be made runnable cheaply (a query, a cost model with inputs), make it so; it then breaks in
  front of the reader, not by argument.
- Aspects are the system's own qualities, named plainly: "Survives a part going down", "A new person can change
  it", "Cheap to run", "Easy to undo".
- The diagrams follow the artifact-diagramming skill where it is available.

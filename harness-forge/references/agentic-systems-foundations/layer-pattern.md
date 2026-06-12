# Pattern Layer — What Has Worked in This Context Before

`Cell: ontology.fleet.layer-pattern · Status: defined · Register: established (Alexander/GoF, case-based reasoning); inversion techniques are house practice`

## Pattern Layer Definition

A pattern is precedential knowledge: a reusable solution shape indexed by the problem
context in which it has worked, distilled from experience rather than derived from
first principles. Patterns are the compression of the ledger — what survives when
trace detail is boiled down to transferable form.

Lineage: Alexander's pattern language and the GoF tradition (a pattern names a
problem-in-context, forces, a solution shape, and consequences); case-based reasoning
(retrieve a similar case, adapt, retain the outcome).

## Patterns Are Distilled, Not Authored

The pattern layer sits last in the partial order because precedent requires
operation: patterns are produced by distilling ledger windows, not by writing down
what ought to work. A "pattern" with no signal-bearing precedent behind it is a
hypothesis and belongs in a spec or methodology cell until experience promotes it.
Each pattern carries its provenance: the ledger entries it was distilled from.

## Anti-Patterns and Content Inversion

Failure catalogues are patterns with the sign flipped, and often higher-leverage:
a named failure mode with its mechanism and corrective transfers across contexts
better than a success story. Content inversion goes further — a failure-mode
catalogue *is* a rubric in disguise: each anti-pattern becomes a scoring dimension
("does the candidate exhibit X?"). The pattern and rubric layers trade material
through this inversion.

## Exemplars as Patterns

Few-shot scored examples — the calibration sets that keep evaluators honest — are
patterns serving the rubric layer: precedents of what each score band looks like.
Seed corpora shipped in family kits are patterns serving cold-start: precedent
imported from outside the project's own ledger, marked as such.

## Pattern vs Methodology Boundary

Methodology is the general procedure for orchestrating any work; a pattern is a
known-good solution shape for a recurring problem. Methodology says how to run the
loop; patterns say what shapes the loop should reach for in context C.

## Pattern vs Heuristic Distinction

Heuristics are defeasible rules of thumb — patterns without the case index. They are
stored in the pattern layer, marked by their weaker evidential grade, not elevated to
a separate layer.

## Pattern Artifact Forms

Pattern entries (context, forces, shape, consequences, provenance refs); anti-pattern
catalogues; few-shot exemplar sets with scores; playbooks; seed corpora with import
provenance.

## Pattern Validation Signal

A pattern cell is `validated` when it has been retrieved and applied in at least one
subsequent engagement with the outcome ledgered — precedent confirmed as transferable,
not merely recorded.

## Pattern Failure Modes

Authored "patterns" with no precedent (hypotheses wearing pattern clothing). Patterns
without provenance (untraceable to ledger evidence; unfalsifiable). Stale patterns
(context moved; the shape now misleads — staleness propagation applies here too).
Pattern hoarding (corpora that grow but are never retrieved at selection or
generation time).

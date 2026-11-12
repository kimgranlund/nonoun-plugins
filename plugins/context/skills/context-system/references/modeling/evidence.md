# Assertions, evidence and uncertainty

Use when knowledge is extracted, reconciled, derived or disputed. Provenance
explains where a claim came from; it does not prove the claim true.

## Preserve the claim and its conditions

Keep source-native assertions separately identifiable from local interpretations,
computations and observations. A useful claim record identifies its subject,
property/relation, value or object, source locator and revision, and the context
needed to interpret it. Add method, time or units where they change the meaning.
Do not demand fields that the source cannot establish; record that limitation.

For consequential claims, retain a precise excerpt/location or immutable evidence
reference sufficient to recheck the interpretation. If source bytes change, a hash
can detect drift but cannot explain the semantic change. Do not invent retrieval
timestamps, measurements, source quotations or confidence values.

Distinguish these questions:

- What does the source actually assert?
- What did a transformation infer or calculate, using which inputs and rule?
- What did an observation measure, under which conditions and method?
- Which interpretation or policy did the project adopt for the intended use?

## Missingness and conflict

Missing, unknown, not applicable, explicitly absent and zero are different states.
Choose the local representation that preserves the distinction. A null by itself
may need a reason/status; a boolean field may need an unknown state. In an
open-world model, failure to find a statement does not establish its negation.

Retain contradictory claims with their sources and scopes. Check whether different
definitions, releases, measurement methods, time periods or populations explain
the disagreement before calling it a factual conflict. If the project resolves it,
record the evidence and decision; do not overwrite the rejected source claim.

A similarity score measures what its method defines, not necessarily probability
of correctness. Use qualitative uncertainty when no calibrated numerical measure
exists. Keep evidence confidence, mapping status and fitness for a downstream use
as separate concerns.

## Derived facts

Record the exact inputs, versions, context and transformation for a derivation.
Check semantic compatibility as well as arithmetic: equal units do not make a
minimum, maximum, target and observed value interchangeable. Derived artifacts
must remain traceable to authored inputs; correcting a generator is different
from promoting a new source interpretation.

When evidence is unavailable, return the narrow supported conclusion and the
specific missing evidence. Do not convert uncertainty into either automatic
acceptance or blanket rejection of independent, supported neighboring decisions.

## Basis

[PROV-O](https://www.w3.org/TR/prov-o/) supplies entity, activity, agent, attribution,
derivation and revision concepts. Using similar distinctions locally does not by
itself make a JSON record a conforming PROV-O serialization.

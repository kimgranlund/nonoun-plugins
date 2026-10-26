# Validation and repair

Applies to: runtime harness.

Observed in a five-round study of one runtime harness that renders generative UI, not universal law. Format and the other files: [README](README.md).

17. Add semantic checks beyond the schema.
    - Observed in the five-round study: a schema-valid payload stated a total that contradicted its own cards; only a domain check caught it.
    - Check: seed one schema-valid, self-contradictory payload per domain and confirm a check fires.
    - Applies to: runtime harness.
18. Repair text is a prompt: frame it as a check result and ask for a shape that passes the schema.
    - Observed in the five-round study: a small model called a repair message "a fabricated system notice" and refused; a repair asking for a reference number it could not have read as a request to fabricate.
    - Check: each repair message names the failing code, the expected shape, and asks for nothing the model cannot produce.
    - Applies to: runtime harness.
19. Checks must not contradict each other on one turn.
    - Observed in the five-round study: one check demanded a booking form and another rejected it on the same turn, and the repair loop ended uncorrected.
    - Check: run every pair of checks that can fire on one moment against one payload; at most one demands a change.
    - Applies to: runtime harness.
20. Judge the final turn as a whole, not the last repair round.
    - Observed in the five-round study: a repair round accepted a reply with no surface, and the next check fired against a surface that no longer existed.
    - Check: a test where round 2 drops the surface shipped in round 1 is not accepted.
    - Applies to: runtime harness.
21. Show users codes, not internals.
    - Observed in the five-round study: a halt message named an internal surface id to the user.
    - Check: grep user-visible halt and error text for internal ids and check codes; only the documented code appears.
    - Applies to: runtime harness.
22. Lints follow the design system's own exemptions.
    - Observed in the five-round study: a type-floor lint failed every turn of one composite whose small corner index the design system already treated as pictorial.
    - Check: each lint rule cites the design rule it enforces and lists that rule's exemptions.
    - Applies to: runtime harness.

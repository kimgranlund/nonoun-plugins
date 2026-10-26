# Guidance authoring

Applies to: mixed, tagged per lesson.

Observed in a five-round study of one runtime harness that renders generative UI, not universal law. Format and the other files: [README](README.md).

12. Small models follow general rules literally, including where they collide with a specific case.
    - Observed in the five-round study: a small model refused to confirm a complete booking because a general rule said the user takes the final action; a larger model confirmed in one round.
    - Check: for each general rule, list the cases it must not cover and test one of them on the smallest model.
    - Applies to: both.
13. Settle each guidance conflict in one place, and have every other layer point to it.
    - Observed in the five-round study: a services list split between two composites because persona text and a shared skill each claimed it; the fix needed a ruling first.
    - Check: grep the rule's key phrase across persona text, shared grammar and skills; it is stated once.
    - Applies to: both.
14. Fix per agent before the shared layer.
    - Observed in the five-round study: shared grammar edits for one persona's failure risk every other persona; persona text and that persona's checks were the narrower lever.
    - Check: the change touches the shared grammar only when two or more agents fail the same way.
    - Applies to: runtime harness.
15. A "use composite X" or "update the surface" rule is a hint until a check backs it.
    - Observed in the five-round study: prose alone moved composite choice on 1 of 24 and 0 of 28 turns for two personas; a generated missing-composite check repaired both.
    - Check: every such rule has a deterministic check whose code appears in the repair round.
    - Applies to: runtime harness.
16. Generate derived prompt assets from one source and drift-gate them.
    - Observed in the five-round study: hand-copied lists drifted between the prompt and the checks, so a check judged a shape the prompt never asked for.
    - Check: a freshness test fails when the generated file differs from its source.
    - Applies to: both.

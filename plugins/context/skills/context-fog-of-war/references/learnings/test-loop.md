# Test loop

Applies to: mixed, tagged per lesson.

Observed in a five-round study of one runtime harness that renders generative UI, not universal law. Format and the other files: [README](README.md).

23. Run live rounds under a spend cap, cheapest model first, and rerun only failures.
    - Observed in the five-round study: five capped rounds stayed within budget and a cap stop still left the cheap cells filled.
    - Check: the runner refuses to start without a cap and skips runs that already have a result.
    - Applies to: runtime harness.
24. Turn every live failure into a keyless replay pinned to its failing checks.
    - Observed in the five-round study: replays pinned red flipped green with their fix, which proved the fix without another paid round.
    - Check: the replay suite runs with no provider key and fails on a network call.
    - Applies to: runtime harness.
25. Oracles must be specific.
    - Observed in the five-round study: two of five clusters in one round were oracle or scenario defects (an ask with no single right answer, one check too many).
    - Check: each scenario step names exactly one acceptable composite or code, and a second reviewer agrees it is the only right answer.
    - Applies to: both.
26. An authored repaired round proves mechanics, not live compliance.
    - Observed in the five-round study: a hand-built round showed the check and repair firing, but later live turns still answered in prose.
    - Check: claims about model behavior cite a live run, not an authored fixture.
    - Applies to: runtime harness.
27. One cause per ticket, with a failing test first.
    - Observed in the five-round study: tickets split by root cause rather than symptom closed with one keyless test each.
    - Check: the ticket names one cause class and one test that is red before the change.
    - Applies to: both.

# Triage

Applies to: both.

Observed in a five-round study of one runtime harness that renders generative UI, not universal law. Format and the other files: [README](README.md).

6. Rule out lost context first, then classify.
   - Observed in the five-round study: both detailed rounds ruled out lost context before any other analysis, which kept fixes off the transport layer.
   - Check: the run's `retrieved-not-submitted`, `tool-result-not-propagated` and `truncation` coverage is `assessed-no-signal` before any finding blames guidance.
   - Applies to: both.
7. Classify every failure into one cause class: (a) exposure, (b) conflicting or ambiguous guidance, (c) model ignored clear guidance, (d) check, oracle or scenario defect.
   - Observed in the five-round study: about half the failures in one round were (d), not model behavior; fixing the model side would have changed nothing.
   - Check: every row of the why-and-fix table names one primary class and the evidence that excludes the others.
   - Applies to: both.
8. Assign a failed run to every cluster it fails in, and report "any" and "only" counts.
   - Observed in the five-round study: 8 of 26 failed runs in one round failed on two or three clusters; single assignment hid the overlap.
   - Check: the sum of "only" counts plus multi-cluster runs equals the failed-run total.
   - Applies to: both.
9. An index-only guidance entry reaches the model as one line; editing its body cannot move a live turn.
   - Observed in the five-round study: both skills that taught the expected composite were index-only on every turn of a round, so the fix had to change loaded guidance.
   - Check: before editing a skill, confirm its load mode on the failing turn is full.
   - Applies to: both.
10. A content change can create failures elsewhere.
    - Observed in the five-round study: adding an item to a list made a scenario ask ambiguous, and the model asked a clarifying question the oracle scored as a failure.
    - Check: rerun the previous round's passing scenarios that touch the changed content.
    - Applies to: both.
11. Class (c) only when the guidance was framed in full and a larger model passed on the same framing.
    - Observed in the five-round study: the small model sent a move in prose while a larger model on identical framing updated the surface; more context could not help.
    - Check: show the identical framed ids and load modes for the passing and failing turns.
    - Applies to: both.

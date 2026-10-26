# Instrument

Applies to: both (lesson 3 is runtime harness only).

Observed in a five-round study of one runtime harness that renders generative UI, not universal law. Format and the other files: [README](README.md).

1. Record what retrieval returned and what the request actually framed, per turn, as two lists.
   - Observed in the five-round study: comparing the two lists on every line ruled out dropped exemplars across 217 and 169 assessed lines in two rounds, so triage moved on in minutes.
   - Check: one trace line carries both id lists, and a seeded line that drops one id raises `retrieved-not-submitted`.
   - Applies to: both.
2. Record tool results received and tool results submitted to the next request.
   - Observed in the five-round study: all integration tool results reached the next request in both rounds that had them, which removed a whole cause class.
   - Check: a seeded omission raises `tool-result-not-propagated`; zero eligible pairs means the field is missing, not that nothing was lost.
   - Applies to: both.
3. Record the completion state and a run id on every line, including halts and repair rounds.
   - Observed in the five-round study: a halted line declared no complete request list, so one detector could only report `partial` for that round.
   - Check: every line, halted or not, has a run id, a round count and a final state.
   - Applies to: runtime harness.
4. Record each guidance entry's load mode (index line or full body) and the revision of the text, not only section sizes.
   - Observed in the five-round study: the trace kept section sizes but not text, so the exact sentence a model followed had to be inferred from source at a pinned commit.
   - Check: given a failing line, you can name the exact persona text and shared grammar revision it saw without reading git history.
   - Applies to: both.
5. Keep the model's reasoning text and read it before classifying.
   - Observed in the five-round study: once reasoning was kept, the small model named the rule it followed on most failing turns, which moved those failures from "ignored guidance" to "conflicting guidance".
   - Check: for each failed turn, quote the reasoning sentence that names a rule, or record that none exists.
   - Applies to: both.

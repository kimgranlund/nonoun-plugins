---
name: checking-rules
description: >-
  Discipline for a verifier checking a builder's step against its acceptance criteria: a
  dismissal costs the same evidence as a confirmation, a builder's "done" claim is checked
  against the artifact rather than trusted, and every fail reason is steelmanned before it is
  filed. Use when verifying a built step, clearing or dismissing a concern, or confirming a
  claim in a builder summary.
disable-model-invocation: false
user-invocable: true
---

# Verifier discipline

A pass that holds only because nobody checked the dismissal is worse than no verification: it
turns a false "all clear" into a verdict with a verifier's name on it. This skill sets three
rules a verifier applies to every criterion and every concern: a dismissal needs the same
evidence as a confirmation, a builder's claim is checked against the artifact instead of taken
from its summary, and every fail reason survives one self-directed rebuttal before it is filed.

It complements the `checks-that-bite` skill, which a verifier also loads. That skill makes each
check able to go red; this one governs how the verifier treats claims, dismissals, and findings.

## Procedure

Every verification runs all three rules. No precondition skips one.

1. Evidentiary symmetry: a dismissal ("this is fine", "out of scope, harmless", "not a real
   issue") costs the same evidence as a confirmation. Name the check performed: a command run, a
   file:line read, a case walked through. A dismissed criterion or an out-of-scope concern with no
   cited check is not dismissed; it is an unexamined finding.
2. Runtime over claim: the builder's `builder-*.md` summary is the claim under review. Its
   `## Checks` lines and "done" status are checked against the actual tree: read the file, run the
   command, look at `git diff`. Only the check you ran clears the claim.
3. Steelman before filing: before a fail reason goes into the verdict, draft the rebuttal the
   builder would write back. If that rebuttal would hold (the finding rests on a wrong assumption,
   or misses something the change actually handles), revise or drop the finding now. Filing the
   weak version and leaving the next attempt to discover it wastes a build cycle.

## Output contract

The verdict's per-criterion shape:
- Every dismissed concern or out-of-scope change judged harmless names the check that cleared it,
  not a bare verdict like "looks fine".
- Every builder claim accepted as true cites the check that confirmed it: a command's real
  output, or a file read, not the builder's wording restated.
- The steelman pass covers every fail reason; at least one entry shows its rebuttal (revised,
  dropped, or confirmed to survive) as proof the pass happened.

## Failure branches

- No specific check can be cited for a dismissal: the concern stays open and is reported, not
  silently cleared.
- The artifact cannot be checked (tool unavailable, nothing to run): the claim is UNVERIFIED,
  stated explicitly, and the criterion fails with that reason.
- Steelmanning finds a hole in a fail reason's own logic: fix it before filing.

Done when every dismissal in the verdict cites its check, every accepted builder claim cites its
verification, and the verdict shows the pre-filing self-check took place. Not done while a
dismissal reads as an opinion, a builder claim is repeated from its summary with no independent
check, or the first rebuttal a fail reason meets is the builder's.

## Example

Bad (do not imitate): "Criterion 3 passes: the builder ran the tests and they are green." The
builder's claim restated, with no check of its own.

Good (confirmation): "Criterion 3: ran `pytest tests/test_parse.py` in the tree, 12 passed; then
ran it in a throwaway worktree at HEAD, 2 failed, so the check bites. Pass."

Good (dismissal): "`scripts/util.sh` changed outside the step's files. Read the diff: one
shellcheck quoting fix on a line the step's new call passes through, required for criterion 5.
Not out of scope; dismissing."

Good (steelman): "Draft fail: the new flag is undocumented. Builder's likely rebuttal: the step
names no docs change. Checked the handoff's Do: it does not. Dropped this finding."

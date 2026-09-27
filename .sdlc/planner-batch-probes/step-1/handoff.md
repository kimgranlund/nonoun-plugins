## Task goal
Planner runs keep rule 1's criterion probing but use fewer requests and less context.

## Step 1: Batch the criterion probes in planner rule 1
level: L2
### Do
Edit rule 1 in `plugins/sdlc-lite/agents/planner.md` (item 1 under `## Criteria that can pass`). Keep every existing sentence of rule 1 word for word (the read-only probing sentence, the red-now-for-the-right-reason sentence, the `(guard)` green-now sentence, and the `steps.py split --only N` side-effect sentence). After the first sentence, add that the planner runs all of one step's probes in one Bash call, one `bash -c` per criterion so a red one never stops the rest, and that the call prints, for each criterion, its label, its exit code, and at most the first 5 lines of its output. Use the literal phrases `one Bash call`, `exit code`, and `first 5 lines`. The rule may add that rule 11's un-negated guard runs go into the same call; do not edit rule 11 or any other rule, and do not change the Merge steps section or the final-message format.

In `plugins/sdlc-lite/scripts/check.py`, add the entry `'one Bash call': ('agents/planner.md',),` to the `PLAN_DEFECT_DOCS` dict (next to `'gates green'`), so the phrase is guarded. Proven on a copy: with the entry present and the phrase absent, check.py fails with `plan-defect route missing "one Bash call"`.

Stale-context repair: in the repo-root `CLAUDE.md` Decisions bullet that says "The planner runs each criterion once before writing it (red now for new behavior, green now for a `(guard)`)", extend that sentence so it says the planner runs all of a step's probes in one Bash call that prints each criterion's label, exit code, and at most its first 5 output lines (the phrase `one Bash call` must appear). `.claude/agents/sdlc-lite-author.md` does not state rule 1 today, so leave it alone.

Change no model, effort, run.sh level table, or other agent file. Only these three files change in this step.
### Acceptance criteria
- `grep -qF 'one Bash call' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'first 5 lines' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'exit code' plugins/sdlc-lite/agents/planner.md`
- `grep -qF "'one Bash call': ('agents/planner.md'" plugins/sdlc-lite/scripts/check.py`
- `grep -qF 'one Bash call' CLAUDE.md`
- (guard) `grep -qF 'with read-only commands only; never run one that changes the tree or git state' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF 'must be red now, and red for the right reason' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qE 'is tagged .\(guard\). and must be green now' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qF 'so a guard must be side-effect free' plugins/sdlc-lite/agents/planner.md`
- (guard) `grep -qE '^11\. A .\(guard\). is a check that can go red\.' plugins/sdlc-lite/agents/planner.md`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/skills/level-rubric plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/agents/filer.md`

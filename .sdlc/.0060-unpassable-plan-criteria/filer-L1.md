<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0060: Catch plan criteria that can't pass before the build and send plan defects to a replan

## PR body
### Summary
If a plan's acceptance criterion cannot pass, it should be caught before the build starts. If one gets through, the builder, the verifier, or the split lint marks it with the literal prefix `plan defect:`, and that tag sends the task to a planner L3 replan. It never triggers a rebuild or a level bump. The plan built here is `planner-L3.md`. It replaced `planner-L2.md` after the conductor's pre-build review found that two of the L2 plan's own criteria contradicted each other.

### Changes
**Step 1: `steps.py` lints criterion commands**
- `scripts/steps.py`:
  - New `lint_steps` check. It takes each command-like code span under `### Acceptance criteria` and runs it through `bash -n -c --`, so it is parsed but never executed. Placeholders are replaced first, and prose, paths, and flag fragments are skipped.
  - `split` runs this lint before writing anything. It refuses a plan whose criteria do not parse, and the refusal ends with `plan defect: replan this step (/chain 3)`.
  - New `lint <planner.md | task dir>` subcommand that writes nothing.
  - New fixtures `BROKEN_CRITERION` and `BROKEN_PLAN`, and selftest cases (j) to (m).
- `skills/plan/SKILL.md`: `/plan` now runs `steps.py lint` on its result and reports a refusal as a plan defect.
- `CLAUDE.md`: the `steps.py` layout bullet is updated.

**Step 2: a plan defect routes to a replan**
- `agents/planner.md` gains a new "Criteria that can pass" section:
  - Every criterion is red now, or green now if tagged `(guard)`.
  - A step's criteria must be able to hold at the same time.
  - Checks over a whole file or repo pass on "no new findings versus the base commit".
  - No deliberately broken command goes in a criterion code span.
  - A replan reads `## Plan review` and the plan-defect notes in `step-*/`.
- `agents/builder.md`: when a criterion is defective, Status is blocked and Notes starts with `plan defect:`.
- `agents/verifier.md`: when a criterion cannot pass, the verdict is fail and `## For the next attempt` starts with `plan defect:`.
- `agents/conductor.md`: a `plan defect:` note means a planner L3 replan, never a rebuild or a bump.
- `skills/chain/SKILL.md`:
  - Step 3: a split refusal is recorded under `## Plan review`, then planner L3 reruns. After the second refusal, `/chain` stops and asks the user.
  - 4.2: a blocked builder is never rerun.
  - 4.4: a fail tagged `plan defect:` takes the replan path and does not count as a fail.
- `skills/level-rubric/SKILL.md`: a tagged fail or block never counts toward a bump. No model or effort cell changed.
- `skills/handoff-format/SKILL.md`: the task handoff template gains an optional `## Plan review` section.
- `scripts/check.py`: new `PLAN_DEFECT_DOCS` guard that fails when the route's phrases go missing from these docs.
- `CLAUDE.md` gains a Decisions bullet, and the escalation sentence now names the split lint as the one code gate.
- `.claude/agents/sdlc-lite-author.md` gains an invariant to keep the route in sync across its files.

### Verification
Both steps: builder L3, then verifier L2 (Fable medium), and both verdicts are pass.
- Step 1:
  - The selftest passes with ok lines for (j) to (m).
  - Negative control: with `lint_steps` stubbed out, the selftest exits 1, and only case (j) fails.
  - Splitting `BROKEN_PLAN` exits 1 with `plan defect` on stderr and writes no `step-1`. At HEAD the same split succeeded.
  - `lint` passes on this task's own `planner-L3.md`.
  - `check.sh` passes.
  - The builder also ran `lint` on the 42 existing plans. It flagged 3, each a span cut short by a backtick inside it.
- Step 2:
  - `check.sh` passes.
  - Negative control: renaming the tag in a copy of `verifier.md` makes `check.py` exit 1 with a FAIL line naming `agents/verifier.md`. The unedited copy passes.
  - Greps confirm the tag is present in every required doc.
  - `run.sh` is unchanged.
  - Live run: the verifier built a throwaway worktree with a step whose two criteria contradict each other, then ran builder L1 on it. The builder reported `blocked`, and its Notes started with `plan defect:`.
  - Red control for the live run: the builder.md at HEAD also blocked, but its Notes did not start with the literal tag.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `steps.py split` now refuses a plan whose criterion commands do not parse under `bash -n`. A new `steps.py lint` runs the same check without writing anything.
- A `plan defect:` note from the builder, the verifier, or a split refusal now sends the task to a planner L3 replan instead of a rebuild or a level bump. `check.py` fails if the route's wording goes missing from any of its docs. (T-0060)

## Follow-ups
- Add a `steps.py next <step dir>` helper that reads the newest builder and verifier results through `order.py` and prints the next action. Today the plan-defect route is followed only by instruction in `/chain` and the conductor. That same channel was ignored in the second T-0060 report.
- Criteria that contradict each other, and criteria that are not red now, are caught only by the planner prompt. The static lint would not have caught T-0029's stray quote, which sat inside a double-quoted pattern and still parsed. Consider a code check that runs `(guard)` criteria against the current tree before the split.

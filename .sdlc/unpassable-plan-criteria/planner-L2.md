<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Stop plan criteria that can never pass: `steps.py split` refuses a plan whose criterion commands don't parse, the planner proves every criterion can fail today and pass once the step is done, and any builder or verifier report tagged `plan defect:` goes to a replan instead of a rebuild or a level bump.

## Step 1: steps.py refuses criterion commands that do not parse
level: L3
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- Add a `lint_steps(plan, steps)` check. `split` calls it after `parse_steps` and before the step-dir refusal loop, so every check still runs before any write.
- For each step block, take only the lines under `### Acceptance criteria`, up to the next `###`/`##` heading or the end of the block.
- In those lines, find every single-backtick span (`` `...` ``) that contains whitespace. Run each one through `bash -n -c <span>` with `subprocess.run`, no shell, a 5 s timeout, and no execution. Spans without whitespace are skipped: they are file names or identifiers.
- Any nonzero exit raises `Fail`. The message names the plan file, the step number, the span, and bash's stderr. It ends with `plan defect: replan this step (/chain 3)`.
- Add a `lint <planner.md | task dir>` subcommand. It runs the same check and writes nothing: exit 0 prints `steps lint: ok`, exit 1 prints the findings on stderr.
- Update the module docstring to describe `lint` and the new `split` refusal.

Add selftest cases in the same change:
- (j) T-0029's case: a criterion with a stray quote, `` `grep -c 'foo' bar'` ``. `split` refuses, stderr contains `plan defect` and `step 1`, and nothing is written. `lint` exits 1 on it.
- (k) A well-formed multi-word span (`` `grep -c "x" scripts/steps.py` ``) plus a single-token span (`` `scripts/steps.py` ``). Both pass, and `split` writes normally.
- (l) A broken span outside `### Acceptance criteria` (in `### Do`) is ignored.
- (m) `lint` on the good fixture exits 0 and prints `steps lint: ok`.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, and its output includes ok lines for (j), (k), (l) and (m).
- Negative control: turn the `lint_steps` call in `split` into a no-op in a throwaway copy (`git worktree add /tmp/t60 HEAD`, apply the diff, then stub it). The selftest must then exit 1 and name case (j). Remove the worktree afterwards.
- In a temp task dir, with a `handoff.md` holding `## Goal` and a `planner-L2.md` whose step 1 criterion is `` `grep -c 'foo' bar'` ``, `python3 plugins/sdlc-lite/scripts/steps.py split <dir>` exits 1, stderr contains `plan defect`, and no `step-1/` exists afterwards.
- `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/unpassable-plan-criteria` exits 0 on this plan file, once it is saved as `planner-L2.md`.
- `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Step 2: Planner, builder, verifier, and /chain treat plan defects as plan defects
level: L3
### Do
- `plugins/sdlc-lite/agents/planner.md`: add these rules before the output format:
  1. Run each runnable criterion once on the current tree. It must parse, and it must be red now unless it is labeled `(guard)`, meaning it is expected to be green before and after.
  2. Every criterion in a step must be able to hold at the same time (no `solution == HEAD` together with `base == HEAD~1`).
  3. A lint or check over a whole file or repo is scoped by default to "no new findings versus the base commit", for example by comparing against `git worktree add <tmp> HEAD`. It asks for zero findings only when the step's Do fixes the existing ones.
  4. On a replan, read any `plan defect:` note in builder or verifier files and fix that criterion.
- `plugins/sdlc-lite/agents/builder.md`: in rule 3, if the step cannot pass because a criterion is wrong (it doesn't parse, contradicts another, or fails on findings the step didn't cause), set Status blocked and start Notes with `plan defect: <criterion and why>`.
- `plugins/sdlc-lite/agents/verifier.md`: when the work matches the step's intent but a criterion itself cannot pass, the verdict is fail and `## For the next attempt` starts with `plan defect: <criterion and why>`. Otherwise it describes the build defect as now.
- `plugins/sdlc-lite/skills/chain/SKILL.md`:
  - Step 3: if `steps.py split` refuses with `plan defect`, rerun planner L3 on the task handoff with the refusal text in the prompt context, then split again. At most twice, then stop and ask the user.
  - Step 4.4: a fail whose `For the next attempt` starts with `plan defect:` goes to the 4.2 replan path. It never rebuilds, never bumps a level, and doesn't count toward "fail twice".
  - Step 4.2: a blocked builder always replans. Never rerun the same handoff with only `## Previous attempt` added.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md` line 25: a verifier fail tagged `plan defect:` doesn't count toward the bump.
- `plugins/sdlc-lite/agents/conductor.md` line 21: add "plan defect (split refusal, builder or verifier `plan defect:`) → replan, never rebuild or bump".
- `plugins/sdlc-lite/scripts/check.py`: add a doc guard shaped like the long-run check. It fails when `plan defect` is missing from `agents/builder.md`, `agents/verifier.md`, `agents/planner.md`, `skills/chain/SKILL.md`, `skills/level-rubric/SKILL.md`, or `agents/conductor.md`, or when `base commit` is missing from `agents/planner.md`.
- The repo-root `CLAUDE.md` `steps.py` layout bullet: mention `lint` and the plan-defect refusal. `.claude/agents/sdlc-lite-author.md`: keep in sync if it describes steps.py behavior.

### Acceptance criteria
- `plugins/sdlc-lite/scripts/check.sh` exits 0.
- Negative control: in a throwaway worktree with this step's diff applied, delete the `plan defect` sentence from `agents/verifier.md`. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` then exits 1 and prints a FAIL line naming `agents/verifier.md`.
- `grep -n "plan defect" plugins/sdlc-lite/skills/chain/SKILL.md` shows the rule in both step 3 and step 4 (the 4.4 fail branch), and the 4.4 text says a plan-defect fail does not rebuild or bump.
- `grep -n "base commit" plugins/sdlc-lite/agents/planner.md` matches a rule scoping whole-file checks to no new findings, and the same file has the `(guard)` and run-once-on-current-tree rules (observable by reading it).
- `grep -n "plan defect" plugins/sdlc-lite/skills/level-rubric/SKILL.md plugins/sdlc-lite/agents/conductor.md` matches in both files.
- `grep -n "lint" CLAUDE.md` matches in the `steps.py` layout bullet.

## Risks
- The lint only catches criteria that fail to parse (quotes, pipes, EOF), inside multi-word backtick spans. A prose span that doesn't parse as shell, such as `f(a, b)`, is a false positive. The cost is a replan (at most twice, then the user), not a wrong build.
- Criteria that contradict each other (T-0002 step 15) and red-now/green-later proofs are enforced only by the planner prompt, not by code. A planner can still get them wrong. The verifier's `plan defect:` routing is the backstop.
- The plan-defect tag in /chain is followed by instruction, not code, like the rest of escalation. A conductor that ignores it repeats the reported failure. A `steps.py route` helper would enforce it but is out of scope here.
- The second report says builders blocked and /chain still retried. The 4.2 text already said replan, so the root cause there may have been the conductor not following 4.2. Step 2 makes the rule explicit but can't prove the orchestrator obeys it.

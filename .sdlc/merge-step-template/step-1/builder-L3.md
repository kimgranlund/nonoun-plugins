<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/planner.md`: added a `## Merge steps` section between `## Criteria that can pass` and the final-message format. It holds the fill-in rules, the note that criterion 1 still applies (and that no merge step is needed if `<branch>` is already an ancestor of HEAD), and the fenced `merge-step` template.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added a `### Merge step` subsection under `## Step handoff`, just before the `## Previous attempt` paragraph. It says the planner emits the block and `steps.py split` copies it like any other step, followed by the same `merge-step` block, byte-identical to the one in planner.md.
- `plugins/sdlc-lite/agents/builder.md`: added rule 4.
  - A merge step is one whose title starts with `Merge ` and whose Do runs `git merge --no-ff <branch>`.
  - On a merge step the builder merges, resolves conflicts, and creates the merge commit. It never runs `git merge --abort` after resolving and makes no other commit.
  - Uncommitted tracked changes before the merge mean Status is blocked.
  - On every other step it never commits.
  - It never pushes, opens a PR, or publishes, on any step.

## Checks
- Criterion 1 (extract the block, set `<n>` to 1, grep for `## Step 1: Merge `, run `steps.py lint`): printed `steps lint: ok`, exit 0.
- Criterion 2 (each required substring is in the planner block): exit 0, nothing reported missing.
- Criterion 3 (handoff-format block is non-empty and diffs clean against the planner block): exit 0.
- Criterion 4 (`grep -n 'git merge --no-ff' plugins/sdlc-lite/agents/builder.md`): printed 2 lines (10 and 11).
- Criterion 5 (read builder.md): rule 4 states all three rules: commit only on a merge step, no commit on any other step, never push or publish.
- Criterion 6 (`git diff --quiet HEAD -- hooks run.sh steps.py verifier.md`): exit 0.
- Criterion 7 (`bash plugins/sdlc-lite/scripts/check.sh`): exit 0; every selftest passed, plus shellcheck and plugin validate.
- Negative control (my own, not in the criteria):
  - `steps.command_spans` finds 5 command spans in the extracted template, so the lint in criterion 1 is not passing on an empty set.
  - A copy with one span deliberately broken makes `steps.py lint` exit 1 with the `plan defect:` refusal.

## Notes
- Every placeholder in the template (`<branch>`, `<gate command>`, `<tmp>`) passes the lint: `steps.py` swaps it for `PLACEHOLDER` before `bash -n` runs. In the conflict-marker grep, the regex `(<<<<<<<|>>>>>>>)` is partly caught by that placeholder pattern too, but it is inside single quotes, so it still parses. The `<gate command>` span alone is not treated as a command, so it is not linted.
- The block has no blank lines and no line exactly 3 characters long other than its closing fence, so the `sed` range in the criteria ends in the right place.
- `hooks/`, `run.sh`, `steps.py`, and `verifier.md` are untouched.
- Nothing is committed.

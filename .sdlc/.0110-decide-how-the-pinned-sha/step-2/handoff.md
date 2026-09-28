## Task goal
A plan may keep a deliberate ancestry check against a real commit (`git merge-base --is-ancestor <sha> HEAD`) without `steps.py` refusing it, while every other criterion that pins a commit sha is still refused.

## Step 2: Update the docs and run the gates
level: L1
### Do
Describe the exemption in the same words wherever the pinned-sha rule is stated. Only `git merge-base --is-ancestor <sha> HEAD` passes, and every other pinned sha is still refused, including a span that also holds another sha.
- `plugins/sdlc-lite/agents/planner.md` rule 6: add to the last sentence ("`steps.py split` refuses a criterion that pins a commit sha as a `plan defect`") that `git merge-base --is-ancestor <sha> HEAD` is the one allowed form.
- Repo `CLAUDE.md`, the `scripts/steps.py` bullet: extend the parenthetical "(the word `git` plus a 7 to 40 char hex run with a digit and a letter; compare against `HEAD` instead)" with the exemption. In the Decisions bullet, change only the pinned-sha wording, if any.
- `.claude/agents/sdlc-lite-author.md`: in the plan-defect route line, add the exemption after "one that pins a commit sha fixed at plan time".

This is the gates green step. Run `plugins/sdlc-lite/scripts/check.sh` and fix any red that step 1 or this step introduced.
### Acceptance criteria
- `grep '^6\. ' plugins/sdlc-lite/agents/planner.md | grep -q 'merge-base --is-ancestor'`
- `grep -F 'scripts/steps.py' CLAUDE.md | grep -q 'is-ancestor'`
- `grep -F 'pins a commit sha' .claude/agents/sdlc-lite-author.md | grep -q 'is-ancestor'`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

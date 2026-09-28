<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Make the `/file` step 4 publish question name at most 4 options, so `AskUserQuestion` accepts it on the first call.

## Step 1: Cap the publish question at 4 options, with a guard
level: L2
### Do
In `plugins/sdlc-lite/skills/file/SKILL.md` step 4, rewrite the publish question so it names at most 4 options: commit, push, PR, changelog edit. Use the exact phrase "at most 4 options" and say to ask it as one multiSelect question. Drop the GitHub-issues item from that list. Follow-ups are already tickets, so offer them as GitHub issues only in a separate second `AskUserQuestion`, and only when the user wants them published. That question must carry at least 2 options, because a 1-option question is also invalid. Keep the rest of step 4 unchanged: the `hooks/block-publish.sh` note, the numbered-mode folder note, and "Never publish on your own".

In `plugins/sdlc-lite/scripts/check.py`, next to the existing `/file` word check, add a guard for the failing test. It fails with a message when `skills/file/SKILL.md` lacks "at most 4 options", or when step 4 still lists the issues item as one of the publish options. Land the guard together with the SKILL fix.
### Acceptance criteria
- `grep -q "at most 4 options" skills/file/SKILL.md` (run from `plugins/sdlc-lite`; red now because the phrase is missing)
- `grep -q "at most 4 options" scripts/check.py` (red now; the guard names the phrase)
- `python3 scripts/check.py` exits 0 (this is the guard's own check; run against the pre-fix SKILL.md with the new guard applied, it must exit 1 with a FAIL line naming skills/file/SKILL.md)
- (guard) `grep -q "block-publish.sh" skills/file/SKILL.md && grep -q "Never publish on your own" skills/file/SKILL.md`
- (guard) `scripts/check.sh` shows no new findings versus HEAD: run the same command in a `git worktree add <tmp> HEAD` copy and compare.

## Risks
Step 3.3, the follow-ups multiSelect, can also exceed 4 options when a filer file lists many follow-ups. This plan leaves it out of scope, as the ticket does. The "red before, green after" check on the guard needs the builder to apply the check.py edit first and observe the failure. A verifier can only re-run the green end state.

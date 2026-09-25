<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1 (awk on the chain SKILL.md for `open-questions`, `AskUserQuestion` and `[Uu]nattended` after `## 5. File`): pass. Evidence: the command exited 0. Run against `HEAD:plugins/sdlc-lite/skills/chain/SKILL.md` it exited 1, so the check can go red. The new `## 6. Close out` section supplies all three words.
- Criterion 2 (`allowed-tools` line includes `AskUserQuestion`): pass. Evidence: grep exited 0, and the diff shows `AskUserQuestion` appended to the `allowed-tools:` line.
- Criterion 3 (`/sdlc-lite:open-questions` in conductor.md): pass. Evidence: grep exited 0. The same grep against `HEAD:plugins/sdlc-lite/agents/conductor.md` exited 1. The new line sits under the routing list, in the diff at conductor.md:16.
- Criterion 4 (`/open-questions` in CLAUDE.md): pass. Evidence: grep exited 0. The diff adds `/open-questions (batches unresolved items into one AskUserQuestion round; /chain runs it as its close-out)` to the skills bullet.
- Criterion 5 (no em dash in added lines): pass. Evidence: the `test -z` check exited 0. I also read the `git diff` output for all three files and saw no em dash.
- Criterion 6 (observable: interactive branch asks one AskUserQuestion round, unattended branch lists items and never calls it): pass. Evidence: the chain SKILL.md diff shows `Interactive: ask one batched AskUserQuestion round for everything left unresolved.` and `Unattended (headless, no person present): never call AskUserQuestion. List the open items as plain lines in the final report, or say nothing is open.` The "stale, dropped" item is also present. The step 1 skill file `plugins/sdlc-lite/skills/open-questions/SKILL.md` exists but I did not read it, so behavior when the skill actually runs was not observed. The criterion asks about the section's text, which I read.
- Criterion 7 (guard: `check.sh` exits 0): pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` returned rc=0. It ended with `ok: shellcheck` and `ok: plugin validate`, and all the selftests passed. That covers the required words, which are still intact: no check.py failure appeared.
- The provenance line in CLAUDE.md names "harness find-open-questions": pass. Evidence: seen in the CLAUDE.md diff.
- The Do steps also required leaving `.claude/agents/sdlc-lite-author.md` unchanged: pass. Evidence: it does not appear in `git status`.

## Out of scope changes
The diff touches only the three files the step named: chain/SKILL.md, conductor.md and CLAUDE.md. The other worktree changes are `.sdlc/chain-open-questions-sweep` task artifacts, the handoff edit, and the untracked `skills/open-questions/`. Those belong to the task and to step 1, and the step 1 directory is not part of this step's diff. I did not check whether the `handoff.md` edit was needed.

## For the next attempt
None

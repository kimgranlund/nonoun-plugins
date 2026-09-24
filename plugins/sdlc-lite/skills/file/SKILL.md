---
name: file
description: Draft the records for a finished task (PR title and body, changelog entry, follow-ups) from its .sdlc artifacts, then publish only what the user approves.
argument-hint: <.sdlc/task dir>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*), Read, Grep, Glob
---
Arguments: `$ARGUMENTS`

1. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh filer L1 <task dir>/handoff.md` from the project root.
2. Read the result. Show the user the Warnings, the PR title, and the changelog entry.
3. Close the ticket, only if the task `handoff.md` opens with ticket front matter (skip otherwise):
   1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <slug>`, where `<slug>` is the task dir name.
   2. If it refuses because the filer's Warnings are open, show the warnings and ask with AskUserQuestion whether to force-close ("Leave open" recommended first). Rerun with `--force` only if the user approves. On any other refusal, report stderr.
   3. Report the follow-up idea tickets it created.
4. Publishing (commit, push, PR, changelog edit) is outward-facing: ask the user with AskUserQuestion which items to publish, then do only those. Follow-ups are now tickets, so offer them as GitHub issues only as an optional item, and file them only if the user selects it. Never publish on your own. `hooks/block-publish.sh` does not guard this session, since it only fires when `SDLC_ROLE` is set by `scripts/run.sh`; the AskUserQuestion approval here is the only publish gate in the user's own session.

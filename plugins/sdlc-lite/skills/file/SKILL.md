---
name: file
description: Draft the records for a finished task (PR title and body, changelog entry, follow-ups) from its .sdlc artifacts, then publish only what the user approves.
argument-hint: <.sdlc/task dir>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Read, Grep, Glob
---
Arguments: `$ARGUMENTS`

1. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh filer L1 <task dir>/handoff.md` from the project root.
2. Read the result. Show the user the Warnings, the PR title, and the changelog entry.
3. Publishing (commit, push, PR, issues, changelog edit) is outward-facing: ask the user with AskUserQuestion which items to publish, then do only those. Never publish on your own. `hooks/block-publish.sh` does not guard this session, since it only fires when `SDLC_ROLE` is set by `scripts/run.sh`; the AskUserQuestion approval here is the only publish gate in the user's own session.

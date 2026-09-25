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
   1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <slug> --dry-run`, where `<slug>` is the task dir name. It lists each proposed follow-up as `<i>. <title> [<slug>]`, marks any `duplicate of T-NNNN`, and writes nothing. Its last line is `expect <digest>`; keep that digest. If it refuses because the filer's Warnings are open, show the warnings and ask with AskUserQuestion with three options, in this order: "Leave open" (recommended): stop; "Acknowledge with a reason": the user supplies the why, then add `--ack-warnings "<why>"` to every later call (dry run and real close); "Force close": add `--force` to every later call. An unattended run stops on open warnings and never acks or forces. If the refusal names another worktree holding the filer record, tell the user to commit or copy it from there into this tree, then rerun the dry run. On any other refusal, report stderr and stop.
   2. Read the task's artifacts (plan, builder, and verifier files). Mark for dropping any follow-up they already resolve, with a one-line reason each. Items marked `duplicate of` are skipped by close automatically.
   3. When a person is present, ask with AskUserQuestion (multiSelect) which follow-ups to file. Put the recommended set first: the non-duplicate items minus the artifact-answered ones.
   4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <slug> --skip <unselected indices> --expect <digest>`, or plain `close <slug>` (no token) if nothing is skipped. If close refuses with `does not match`, the filer file changed: rerun the dry run and ask again. Do not retry with the new digest blindly.
   5. Unattended (no one to answer): file the non-duplicate follow-ups minus the artifact-answered ones (`--skip` the dropped indices, with `--expect <digest>`), and state that choice and the reasons in the report.
   6. Report the tickets created, the duplicates skipped, and the items dropped, with reasons.
4. Publishing (commit, push, PR, changelog edit) is outward-facing: ask the user with AskUserQuestion which items to publish, then do only those. Follow-ups are now tickets, so offer them as GitHub issues only as an optional item, and file them only if the user selects it. In numbered mode the folder becomes `.NNNN-<slug>` after close. Never publish on your own. `hooks/block-publish.sh` does not guard this session, since it only fires when `SDLC_ROLE` is set by `scripts/run.sh`; the AskUserQuestion approval here is the only publish gate in the user's own session.

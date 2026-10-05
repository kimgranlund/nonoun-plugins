## Task goal
State in every place that describes the mailbox messenger that a subagent can report only into a running parent turn and cannot wake an idle host, with the tested workaround, and record a dated correction note.

## Step 1: Add the idle-host limit to the five places and the note
level: L2

### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/0180-idle-host-limit-docs/handoff.md`

### Do
Edit only these files. (1) `plugins/sdlc-lite/scripts/messages.py`: extend the `## Host limits` section of `ENTRY_TEMPLATE` (keep every existing sentence and command) with the limit; also add one sentence to the module docstring near the Messenger or Layout text if a fitting place exists. (2) `plugins/sdlc-lite/agents/messenger.md`: add the limit in the body, one or two sentences. (3) `docs/ticket-stages/design.md`: add the limit to the bus section. (4) `docs/codex-role-execution.md`: add the limit next to the `sdlc-messenger-l1` paragraph. (5) Create `docs/reports/messages-idle-host-limit-2026-10-01.md`: a dated correction note per the ticket Context (date 2026-10-01, the limit, the evidence that the live runs covered only an active parent, the workaround, and that T-0181 and T-0182 address it). (6) Add a one-line link to that note in `docs/README.md` in the same style as its neighbors. Every one of the first five files must contain the exact sentence `cannot wake an idle host`. Use this wording, adapted: "A subagent, including the messenger, can report only into a parent turn that is still running. It cannot wake an idle host on Claude Code or Codex. Keep the parent in an active turn: on Codex run /goal or have the parent wait on the messenger and spawn it again; on Claude Code keep the foreground session working. The live runs covered only an active parent." Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate the Codex agents. Never hand-edit a generated TOML. No em dashes. Do not change any command, flag, or procedure step.

### Acceptance criteria
- `test "$(grep -l 'cannot wake an idle host' plugins/sdlc-lite/scripts/messages.py plugins/sdlc-lite/agents/messenger.md docs/ticket-stages/design.md docs/codex-role-execution.md docs/reports/messages-idle-host-limit-2026-10-01.md | wc -l)" -eq 5`
- `grep -q 'messages-idle-host-limit-2026-10-01.md' docs/README.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/messages.py|plugins/sdlc-lite/agents/messenger.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml|docs/ticket-stages/design.md|docs/codex-role-execution.md|docs/reports/messages-idle-host-limit-2026-10-01.md|docs/README.md" | { ! grep -q .; }`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Previous attempt
The first build failed verification for one reason. The note `docs/reports/messages-idle-host-limit-2026-10-01.md`, in its section on evidence that the limit was not tested, cites `spawn_agent` and `wait_agent` tool calls with raw evidence in `messages-live-run/codex-messenger.txt`. That file holds neither string (`grep -c wait_agent` and `grep -c spawn_agent` both give 0). The source is `docs/reports/messages-live-run.md` line 156, which quotes the Codex parent's rollout files (`spawn_agent`, `wait_agent`, `followup_task`, `wait_agent`). Fix only the note: cite `docs/reports/messages-live-run.md` (the rollout files paragraph) and drop the `codex-messenger.txt` reference for those tool calls. Check every other file path and quoted string the note cites with grep before you finish. Touch nothing else.

## Task goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

## Step 7: Live run in throwaway repos and the dated validation record
level: L3
### Do
Depends on: steps 1 to 3 (the code under test) and step 6 (the docs/README.md line this step extends). Files: the new `docs/reports/ticket-root-router-live-run.md` and one new list item in `docs/README.md`, placed after the "Plan reviewer live run" item: ``- [Ticket root and router live run](../../../docs/reports/ticket-root-router-live-run.md): dated live run for T-0175 showing the router block change as a ticket moves proposed to ready to done under `ticket_root: tickets`, and a fresh role claiming and closing a ticket from `tickets/AGENTS.md` alone.`` Run everything in `mktemp -d` projects outside this repository, and keep transcripts and logs out of the repository. Write no em dash. Model the doc on `docs/reports/plan-reviewer-live-run.md`.
- Scripted run: this is deterministic, with no model call.
  1. In a fresh git project, write `.sdlc/config` with `ticket_root: tickets` and `ticket_folders: numbered`.
  2. Run `python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc new feature probe "Probe ticket"`.
  3. Set `status: ready` in `.sdlc/tickets/0001-probe/handoff.md` and run `roadmap`.
  4. Write `.sdlc/tickets/0001-probe/filer-L1.md` holding `## Warnings` None and `## Follow-ups` None.
  5. Run `close 0001-probe`, then `check`.
  6. Copy the Stages section of `.sdlc/AGENTS.md` verbatim, in a fenced block, after each of new, roadmap, and close. The three excerpts hold the lines `- proposed: 1`, `- ready: 1`, and `- done: 1`.
  7. State that the folder ended at `.sdlc/tickets/.0001-probe` and that `check` printed `ok`.
- Fresh role (Claude Code):
  1. Set up a second fresh project the same way, with `new`, the status set to ready, and `roadmap`, then commit it.
  2. From that project root, run `claude -p --model sonnet --effort low --dangerously-skip-permissions --output-format stream-json --verbose -- "<prompt>"`, with no `--plugin-dir` and no `--agent`. Run it through the env wrapper of `plan-reviewer-live-run.md`: unset `CLAUDECODE`, every `CLAUDE_CODE_*` variable, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON`. Use the Bash timeout at 600000 or more, in the foreground. Write the log to a file in the temp project, outside this repository.
  3. The prompt is exactly: `Ticket: .sdlc/tickets/0001-probe/handoff.md. Claim this ticket, then close it: its work was already done elsewhere. The sdlc-lite plugin folder is <absolute path of this worktree>/plugins/sdlc-lite.`. It names the plugin folder because the installed plugin caches hold 0.20.1, which has no `ticket_root` (`grep -c ticket_root` of the cached `tickets.py` is 0). It names no skill.
- Record the following from the transcript and the final files:
  - whether the role read `.sdlc/tickets/AGENTS.md` (reached through the handoff's `router:` line);
  - the commands it ran;
  - whether the handoff gained `claimed_by: claude <date>` and the router showed `, claimed by` before the close;
  - whether the ticket ended `status: done` with a `## Closed` section at `.sdlc/tickets/.0001-probe`;
  - whether the router shows `- done: 1`;
  - whether `tickets.py --root .sdlc check` passes;
  - whether any Skill tool call appears.

  Write `Result: verified` when every one holds. Otherwise write `Result: unverified: <what failed>`. When `claude` is missing or not logged in, write `Result: unverified: <the reason>`.
- Doc layout, in this order:
  - `# Ticket root and router live run`
  - a `Recorded: <YYYY-MM-DD>.` line
  - `## Environment`: the Claude Code version, the model from the log's `"model"` field, the plugin commit plus whether the T-0175 changes were uncommitted, and macOS.
  - `## Scripted run`
  - `## Fresh role`: the prompt, the observations, and the `Result:` line.
  - `## Limits`: Claude Code only, Codex not run and not claimed; the prompt named the plugin folder, for the reason above; one trial per arm.
### Acceptance criteria
- `test -f docs/reports/ticket-root-router-live-run.md && grep -qE '^Recorded: [0-9]{4}-[0-9]{2}-[0-9]{2}\.' docs/reports/ticket-root-router-live-run.md`
- `grep -qF '(validation/ticket-root-router-live-run.md)' docs/README.md`
- `grep -qx '## Scripted run' docs/reports/ticket-root-router-live-run.md && grep -qxF -- '- proposed: 1' docs/reports/ticket-root-router-live-run.md && grep -qxF -- '- ready: 1' docs/reports/ticket-root-router-live-run.md && grep -qxF -- '- done: 1' docs/reports/ticket-root-router-live-run.md && grep -qF 'ticket_root: tickets' docs/reports/ticket-root-router-live-run.md`
- `grep -qx '## Fresh role' docs/reports/ticket-root-router-live-run.md && grep -qE '^Result: (verified|unverified: .+)$' docs/reports/ticket-root-router-live-run.md && grep -qx '## Limits' docs/reports/ticket-root-router-live-run.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py|plugins/sdlc-lite/scripts/board.py|plugins/sdlc-lite/scripts/traces/ingest.py|plugins/sdlc-lite/scripts/traces/sources/tickets.py|plugins/sdlc-lite/scripts/traces/selftest.py|docs/maintenance/sdlc-internals.md|plugins/sdlc-lite/skills/handoff-format/SKILL.md|plugins/sdlc-lite/skills/ticket/SKILL.md|docs/ticket-stages/design.md|docs/ticket-stages/README.md|docs/README.md|docs/reports/ticket-root-router-live-run.md" | { ! grep -q .; }`

## Previous attempt (verifier-L2.md)
Only `docs/reports/ticket-root-router-live-run.md` needs a change. No re-run is needed.
- Change the Fresh role `Result:` line from `Result: verified` to `Result: unverified: <reasons>`, giving two reasons that match the doc's own observations.
  - The role did not read `.sdlc/tickets/AGENTS.md` through the handoff's `router:` line. It received it through Claude Code nested-memory loading.
  - The `, claimed by` router state before the close was not captured live. It was reproduced only by replay.
- Keep the rest of the doc. The README line can stay.

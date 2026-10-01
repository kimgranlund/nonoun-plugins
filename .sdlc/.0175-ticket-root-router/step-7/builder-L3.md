<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/validation/ticket-root-router-live-run.md`: new dated live-run record with these sections: Environment, Scripted run, Fresh role, Limits.
- `docs/README.md`: added the "Ticket root and router live run" list item right after the "Plan reviewer live run" item.

## Checks
- Scripted run, in temp project `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/ticket-router-probe.Zipw3u86zW/scripted` (no model call): `new`, set `status: ready`, `roadmap`, write `filer-L1.md`, `close 0001-probe`, `check`. Every command exited 0. The Stages excerpt showed `- proposed: 1` after new, `- ready: 1` after roadmap and `- done: 1` after close. The folder ended at `.sdlc/tickets/.0001-probe`. `check` printed `ok: 1 tickets, roadmap current`.
- Fresh role, in the `.../role` project (committed `53d9fb3 init`):
  - Command: `env -u CLAUDECODE -u CLAUDE_CODE_* ... -u SDLC_* claude -p --model sonnet --effort low --dangerously-skip-permissions --output-format stream-json --verbose -- "<prompt>"`, with no `--plugin-dir` and no `--agent`.
  - It exited 0 after 5 turns, on model `claude-sonnet-5-5` with Claude Code 2.1.286.
  - The log was written to the temp folder, outside the repo.
- Final role state: handoff has `claimed_by: claude 2026-09-30`, `status: done` and a `## Closed` section at `.sdlc/tickets/.0001-probe`. The router shows `- done: 1`, `check` printed ok with exit 0, and the log contains no Skill call.
- Replay of the claim state, in a clone of `53d9fb3`: applied the role's exact edit, then ran `roadmap`. The router showed `, claimed by claude 2026-09-30`.
- Acceptance criteria 1 to 4: each exited 0.
- (guard) changed-file allowlist: exited 0.
- `git diff --check`: exited 0. Both files contain no em dash.

## Notes
- The doc says `Result: verified`, but two of the observations held in a different way than the handoff described. Both are spelled out in the doc's Fresh role and Limits sections; the planner may want to read them as `unverified`:
  1. The role never opened the `router:` path itself. Its one read of the handoff made Claude Code auto-load the nested memory files. The session transcript has `nested_memory` attachments for `.sdlc/tickets/CLAUDE.md` and for `.sdlc/tickets/AGENTS.md` (the latter pulled in through the former's `@AGENTS.md` import). That is how the router procedures reached the role.
  2. The role ran `roadmap && close` in a single Bash call, so the router's `, claimed by` state between the two was never captured live. It is shown only by the deterministic replay above.
- The role closed with `close --reason`, which is the router's step for work already done elsewhere, and it ran no filer.
- The temp projects and role log are left under the mktemp folder above, outside the repo. Nothing was committed.

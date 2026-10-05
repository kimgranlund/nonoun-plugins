# Ticket root and router live run

Recorded: 2026-09-30. Live run for ticket T-0175: with `ticket_root: tickets` in `.sdlc/config`, ticket folders live under `.sdlc/tickets/`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current. One scripted arm with no model call, and one fresh Claude Code role that claims and closes a ticket from the router alone.

## Environment

- Claude Code 2.1.286 (`claude --version`, and `claude_code_version` in the role log). Model from the log's `"model"` field: `claude-sonnet-5-5`, run with `--model sonnet --effort low`.
- Plugin commit `604d7cc` (T-0175 steps 1 to 6), with no uncommitted change under `plugins/`. The T-0175 changes were committed on the `ticket-stages` branch; they are not in a released plugin. The installed plugin caches hold 0.20.1 and older, and `grep -c ticket_root` of each cached `tickets.py` printed 0.
- macOS 26.6.2, Darwin 25.6.0. Two throwaway Git projects in one `mktemp -d` folder outside this repository: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/ticket-router-probe.Zipw3u86zW/scripted` and `.../role`. The role log stayed in that folder and is not kept in this repository.

## Scripted run

Deterministic, with no model call. `<repo>` below is this repository. In a fresh `git init` project:

```sh
printf 'ticket_root: tickets\nticket_folders: numbered\n' > .sdlc/config
python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc new feature probe "Probe ticket"
# set status: ready in .sdlc/tickets/0001-probe/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap
printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/tickets/0001-probe/filer-L1.md
python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc close 0001-probe
python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc check
```

`new` printed `.sdlc/tickets/0001-probe/handoff.md` and wrote `.sdlc/AGENTS.md`, `.sdlc/CLAUDE.md`, `.sdlc/roadmap.md`, `.sdlc/tickets/AGENTS.md`, and `.sdlc/tickets/CLAUDE.md`. The handoff's last front matter line was `router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket`.

Stages section of `.sdlc/AGENTS.md` after `new`:

```
## Stages

- proposed: 1
  - T-0001 Probe ticket (0001-probe)
- ready: 0
- blocked: 0
- done: 0
- dropped: 0
```

After `roadmap` (which printed `wrote .sdlc/roadmap.md`):

```
## Stages

- proposed: 0
- ready: 1
  - T-0001 Probe ticket (0001-probe)
- blocked: 0
- done: 0
- dropped: 0
```

After `close` (which printed `T-0001 done; follow-up ticket: none; 0 follow-up(s) appended to notes.md; moved to .0001-probe`):

```
## Stages

- proposed: 0
- ready: 0
- blocked: 0
- done: 1
- dropped: 0
```

The three excerpts show the lines:

- proposed: 1
- ready: 1
- done: 1

The folder ended at `.sdlc/tickets/.0001-probe` with `status: done`. `check` printed `ok: 1 tickets, roadmap current` and exited 0.

## Fresh role

A second fresh project was set up the same way (`new`, `status: ready`, `roadmap`; `check` printed `ok`) and committed once (`53d9fb3 init`). From its root, with no `--plugin-dir` and no `--agent`:

```sh
W claude -p --model sonnet --effort low --dangerously-skip-permissions --output-format stream-json --verbose -- "<prompt>" > <temp>/role.log
```

`W` is the env wrapper of [plan-reviewer-live-run.md](plan-reviewer-live-run.md): `env -u` for `CLAUDECODE`, every `CLAUDE_CODE_*` variable set in the launching shell, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON`. It exited 0 after 5 turns, 9.8 s, $0.21.

The prompt, exactly:

```
Ticket: .sdlc/tickets/0001-probe/handoff.md. Claim this ticket, then close it: its work was already done elsewhere. The sdlc-lite plugin folder is /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages/plugins/sdlc-lite.
```

Observations, from the stream-json log, the session transcript under `~/.claude/projects/`, and the final files:

- Router read: not through the `router:` line. The role made no Read call on the `router:` path. Its one Read, of `.sdlc/tickets/0001-probe/handoff.md`, made Claude Code load the nested memory files of that path: the session transcript holds `nested_memory` attachments for `.sdlc/CLAUDE.md`, `.sdlc/AGENTS.md`, `.sdlc/tickets/CLAUDE.md`, and `.sdlc/tickets/AGENTS.md`, with the full router text including the Claim and Close procedures. So `.sdlc/tickets/AGENTS.md` reached the role through the `@AGENTS.md` import in `.sdlc/tickets/CLAUDE.md`, next to the handoff, rather than through the handoff's `router:` line.
- Commands, in order: Read `.sdlc/tickets/0001-probe/handoff.md`; Bash `ls <repo>/plugins/sdlc-lite/scripts; ls .sdlc/tickets`; Edit of the handoff adding `claimed_by: claude 2026-09-30` after `created:`; Bash `python3 $P/scripts/tickets.py --root .sdlc roadmap && python3 $P/scripts/tickets.py --root .sdlc close 0001-probe --reason "Work already done elsewhere"`. It ran no filer, matching the router's step for work already done by another ticket.
- Claim: the handoff gained `claimed_by: claude 2026-09-30`. The role's `roadmap` and `close` ran in one Bash call, so the router between them was not captured live. A replay in a clone of `53d9fb3`, applying the role's exact Edit and then `roadmap`, gave the ready line `  - T-0001 Probe ticket (0001-probe), claimed by claude 2026-09-30`.
- Close: `close` printed `T-0001 done (closed by reason: Work already done elsewhere); no follow-ups filed; moved to .0001-probe`. The ticket ended at `.sdlc/tickets/.0001-probe` with `status: done` and a `## Closed` section reading `2026-09-30: Work already done elsewhere`.
- Router after close: the Stages section shows `- done: 1` with proposed, ready, blocked, and dropped at 0. Claude Code's `edited_text_file` attachment for `.sdlc/AGENTS.md` shows the same.
- `python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` printed `ok: 1 tickets, roadmap current` and exited 0.
- Skill tool: no Skill call appears in the log (`grep -c '"name":"Skill"'` printed 0). The tools called were Read, Bash, Edit, Bash.

Result: unverified: the role did not read `.sdlc/tickets/AGENTS.md` through the handoff's `router:` line, it received the router through Claude Code nested-memory loading; the `, claimed by` router state before the close was not captured live, it was reproduced only by replay.

## Limits

- Claude Code only. Codex was not run, and nothing here is claimed for Codex.
- The prompt named the plugin folder, because the installed plugin caches hold 0.20.1, which has no `ticket_root` (`grep -c ticket_root` of the cached `tickets.py` is 0). Without that, the router's `${CLAUDE_PLUGIN_ROOT}` would resolve to a release that cannot read `.sdlc/tickets/`.
- The router reached the role through Claude Code's nested memory loading, not through the `router:` front matter line. The run shows nothing about a host that does not load nested `CLAUDE.md` files, where the `router:` line is the only pointer.
- The `, claimed by` router line was shown by a deterministic replay of the role's own edit, not captured between the role's `roadmap` and `close`.
- One trial per arm, on one machine and one account.

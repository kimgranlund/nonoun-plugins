<!-- sdlc-lite:managed:start v1 sha256:7a19691aa1bb -->
# Work records

This folder holds SDLC Lite `config`, this router, and the git-ignored `runtime/` and `messages/`. Tickets, task records, `docs/work/ROADMAP.md`, and `docs/work/NOTES.md` are in the work root `docs/work/`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `docs/work/ROADMAP.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: `docs/work/`, the work root `work_root:` in `.sdlc/config` names.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.
- No plugin installed: follow `.sdlc/by-hand.md` to create, claim, release or close a ticket with git alone.

## Stages

- proposed: 0
- ready: 0
- claimed: 1
  - T-0797 tickets.py close deletes skips.md and other ticket-folder files (#83) (docs/work/0797-close-keeps-ticket-files), claimed by sdlc-lite-author 2026-10-28
- paused: 0
- blocked: 1
  - T-0611 Rehearse a Pi host working tickets beside Claude and Codex (docs/work/0611-pi-host-rehearsal)
- done: 759
- dropped: 30

## Procedures

Folder layout:
- The top of `.sdlc` holds only `AGENTS.md`, `CLAUDE.md`, `by-hand.md`, `config`, `board.md`, `fleet.json`, `gate-ledger.jsonl`, `messages/`, `runtime/`, `supervisor/`, `evals/`, `proposals/`, `goals/`, `tickets/`, `work/`, `archive/`, and `_`- or `.`-prefixed entries; ticket and task folders go in `docs/work/`. A `top_level_allow: <glob>, ...` line in `.sdlc/config` allows more.
- Run records (role results, attempts, `runs.jsonl`, `skips.md`) go in the git-ignored records dir `.sdlc/runtime/tasks/<folder>/` (`<plugin-root>/scripts/order.py records-dir docs/work/<folder>` prints it). Notes go to `docs/work/NOTES.md`, an answer to another agent goes by `messages.py send`, anything else into `../docs/work/archive/`.
- `python3 <plugin-root>/scripts/tickets.py --root .sdlc check` warns on any other top-level entry; `python3 <plugin-root>/scripts/tickets.py --root .sdlc tidy` lists its move into `../docs/work/archive/` and `python3 <plugin-root>/scripts/tickets.py --root .sdlc tidy --apply` makes it. Move nothing under `.sdlc` while a `*.running` marker exists: a role is using it.

Create a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc new <feature|bug|chore|spike|idea> <slug> "<title>"`. Never pick an id by hand: `new` stamps the next id above every worktree's.
2. Fill in the body sections of the new `handoff.md`.

Ticket fields:
status: proposed | ready | claimed | paused | blocked | done | dropped
- `area:` is optional: the ticket's domain, one of the `areas:` names in `.sdlc/config`. It is never a lane or branch name.
- `paused_reason:` is the one-line reason a `status: paused` ticket waits; `status: claimed` needs `claimed_by:`.
- `branch:` and `worktree:` name the ticket's lane branch and its worktree (relative to the main checkout, under the worktree root `../<repo>.worktrees/`, `wtroot.py root`); the lane opener writes both and its close removes both. `check` warns on a `worktree:` that is not a registered worktree on that branch.

Claim a ticket:
1. Open its `handoff.md`. A `claimed_by:` front matter line means another agent holds it: pick another ticket or ask the user.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc claim <id>`; `--by <agent>` names the claimant and wins, else it takes `$SDLC_HOST`, else the host (`claude:<session8>`, `codex:<thread>`). In git it first reserves `refs/sdlc/claims/<id>`, so a claim from any worktree refuses naming the holder. It sets `status: claimed`, writes `claimed_by: <agent> <YYYY-MM-DD>` directly after `created:`, and runs `roadmap`. To take over a stale claim, add `--handover --reason "<why>"`.
3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> docs/work/<folder>/handoff.md`, or `/sdlc-lite:chain docs/work/<folder>`. Progress shows on `/board`.
4. Release: `python3 <plugin-root>/scripts/tickets.py --root .sdlc release <id>`. Pause: set `status: paused` and add a one-line `paused_reason:`, then rerun `roadmap`.

Open a lane:
1. Claim the ticket first: `<plugin-root>/scripts/lanes.py open` refuses an unclaimed local ticket.
2. Run `python3 <plugin-root>/scripts/lanes.py open <name> --kind solo --ticket <id>`. It makes the worktree and branch under the worktree root (`../<repo>.worktrees/`) and writes `branch: <lane branch>` and `worktree: <path>` after `claimed_by:`, so verified, unmerged work stays visible on the roadmap and in `lanes.py list --all`. A worktree made by hand: run `python3 <plugin-root>/scripts/tickets.py --root .sdlc branch <id> <branch> --worktree <path>`.
3. `lanes.py close <name>` removes the `branch:` and `worktree:` lines once the lane closes.

Close a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run`. It checks the verifier verdict, lists each verifier `## Notes` line as `<i>. <tag>: <title>`, and ends with `expect <digest>`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --changed "<one line>"`. It appends `## Outcome` to the handoff; add `--lessons "<lesson>"` (repeatable) for a reusable lesson, one `- Lessons:` line each: route it to a named repo skill or NOTES.md. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `docs/work/NOTES.md`, where adding ` -> T-NNNN` to an item's line marks it routed (the roadmap lists the rest under Open follow-ups); `fix-now:` items are finished before the close. When it refuses because files cite the folder, add `--rewrite-refs` to rewrite them to the closed `.<folder>` path.
3. Only when a filer draft was asked for (`/file`): `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --filer`.
4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --reason "<why>"`. It skips the verdict gate but files follow-ups as step 2 does: the verifier `## Notes` lines and the handoff `## Follow-ups` bullets go to `docs/work/NOTES.md`, and `--dry-run` and `--ticket <i> --expect <digest>` work the same.

Ticket lifecycle:
1. Pick and claim: `python3 <plugin-root>/scripts/tickets.py --root .sdlc claim <id> --by <agent>`.
2. Lane: `python3 <plugin-root>/scripts/steps.py lane docs/work/<folder>` prints the lane.
3. Build: the solo agent, `/sdlc-lite:fix`, or `/sdlc-lite:chain docs/work/<folder>`.
4. Verify: one independent verifier per ticket (`/sdlc-lite:verify`).
5. Land: `python3 <plugin-root>/scripts/fanout.py land <branch>` for a lane branch, else merge the branch.
6. Close: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --changed "<one line>"`, as in Close a ticket above.
<!-- sdlc-lite:managed:end -->

## Other records

- Evals: `../docs/work/evals/` holds the dated model and effort experiments and `table-lock.json`; read `../docs/work/evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
- Proposals: `../docs/work/proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `../docs/work/proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.

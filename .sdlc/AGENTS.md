<!-- sdlc-lite:managed:start v1 sha256:eb2da9465854 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 12
  - T-0527 Close references, router links, launcher and root guard (maison T-0546) (0527-close-refs-router-launcher)
  - T-0528 Detect delivered and superseded open tickets (maison T-0546) (0528-detect-delivered-tickets)
  - T-0529 Writing rules for work records, and a placeholder gate at close (maison T-0546) (0529-work-record-writing-rules)
  - T-0530 Lane record on the ticket (maison T-0546) (0530-lane-record-on-ticket)
  - T-0531 Run records: retry names, filer prune, empty solo (maison T-0546) (0531-run-record-names-prune)
  - T-0532 Step tooling and long suites (maison T-0546) (0532-step-tooling-long-suites)
  - T-0533 steps.py split lints each step alone: a path an earlier step creates ([creates: ...]) reads as a plan defect (maison T-0546 item 32) (0533-split-lint-creates-marker)
  - T-0534 A layout rule for the top of .sdlc, any agent name in claims, and one ticket lifecycle page (maison T-0546) (0534-sdlc-top-level-layout-and-lifecycle)
  - T-0535 tickets.py close: a marker that excludes an inventory file from the citation scan (maison T-0546) (0535-close-inventory-skip-marker)
  - T-0536 Catch a criterion that needs a later step, and a narrow amend route for a builder-reported plan defect (maison T-0546) (0536-plan-defect-order-and-amend)
  - T-0537 dispatch.py: a sub-agent stopped by the spend limit is resumable, and prepare notes a changed model or effort (maison T-0546) (0537-dispatch-limit-stop-and-row-change)
  - T-0538 Role brief: the result header is added at record time, and cleanup under the tmp prefix is allowed (maison T-0546) (0538-verifier-brief-header-and-tmp-cleanup)
- ready: 0
- claimed: 0
- paused: 0
- blocked: 0
- done: 490
- dropped: 29

## Procedures

Create a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc new <feature|bug|chore|spike|idea> <slug> "<title>"`. Never pick an id by hand: `new` stamps the next id above every worktree's.
2. Fill in the body sections of the new `handoff.md`.

Ticket fields:
status: proposed | ready | claimed | paused | blocked | done | dropped
- `area:` is optional: the ticket's domain, one of the `areas:` names in `.sdlc/config`. It is never a lane or branch name.
- `paused_reason:` is the one-line reason a `status: paused` ticket waits; `status: claimed` needs `claimed_by:`.

Claim a ticket:
1. Open its `handoff.md`. A `claimed_by:` front matter line means another agent holds it: pick another ticket or ask the user.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc claim <id> --by <claude|codex>`. It sets `status: claimed`, writes `claimed_by: <agent> <YYYY-MM-DD>` directly after `created:`, and runs `roadmap`. To take over a stale claim, add `--handover --reason "<why>"`.
3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> .sdlc/<folder>/handoff.md`, or `/sdlc-lite:chain .sdlc/<folder>`. Progress shows on `/board`.
4. Release: `python3 <plugin-root>/scripts/tickets.py --root .sdlc release <id>`. Pause: set `status: paused` and add a one-line `paused_reason:`, then rerun `roadmap`.

Close a ticket:
1. Run the filer (`/file`): `<plugin-root>/scripts/run.sh filer L1 .sdlc/<folder>/handoff.md`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run`. It lists each follow-up as `<i>. <tag>: <title>` and ends with `expect <digest>`.
3. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder>`. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `notes.md`; `fix-now:` items are finished before the close. When it refuses because files cite the folder, add `--rewrite-refs` to rewrite them to the closed `.<folder>` path.
4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --reason "<why>"`.
<!-- sdlc-lite:managed:end -->

## Other records

- Evals: `evals/` holds the dated model and effort experiments and `table-lock.json`; read `evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
- Proposals: `proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.

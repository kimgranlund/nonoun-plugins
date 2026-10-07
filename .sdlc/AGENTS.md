<!-- sdlc-lite:managed:start v1 sha256:1ae64a459b1f -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 5
  - T-0288 Retire the Claude headless execution path (0288-retire-claude-exec)
  - T-0301 Conductor schedules the rerun after a 429 limit (0301-limit-conductor-rerun)
  - T-0316 Live headless chain run on Codex, recorded (0316-codex-live-evidence)
  - T-0317 Verifier policy: a browser-test red under measured load re-runs once alone before it counts (0317-red-under-load-rerun)
  - T-0348 tickets.py close offers a quiet --keep-refs so a doc citing the folder does not force --force (0348-close-keep-refs)
- ready: 0
- blocked: 0
- done: 311
- dropped: 25

## Procedures

Create a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc new <feature|bug|chore|spike|idea> <slug> "<title>"`. Never pick an id by hand: `new` stamps the next id above every worktree's.
2. Fill in the body sections of the new `handoff.md`.

Claim a ticket:
1. Open its `handoff.md`. A `claimed_by:` front matter line means another agent holds it: pick another ticket or ask the user.
2. Add `claimed_by: <claude|codex> <YYYY-MM-DD>` to the front matter, then run `python3 <plugin-root>/scripts/tickets.py --root .sdlc roadmap`.
3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> .sdlc/<folder>/handoff.md`, or `/sdlc-lite:chain .sdlc/<folder>`. `status` stays a person's decision; progress shows on `/board`.

Close a ticket:
1. Run the filer (`/file`): `<plugin-root>/scripts/run.sh filer L1 .sdlc/<folder>/handoff.md`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run`. It lists each follow-up as `<i>. <tag>: <title>` and ends with `expect <digest>`.
3. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder>`. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `notes.md`; `fix-now:` items are finished before the close.
4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --reason "<why>"`.
<!-- sdlc-lite:managed:end -->

## Other records

- Evals: `evals/` holds the dated model and effort experiments and `table-lock.json`; read `evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
- Proposals: `proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.

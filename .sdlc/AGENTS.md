<!-- sdlc-lite:managed:start v1 sha256:1bd145d80d58 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 16
  - T-0193 footprint.py: measure and gate a ticket's footprint (0193-footprint)
  - T-0194 Lean lane text and coarse-step rule in chain and planner (0194-lean-lane-text)
  - T-0195 Runner: verifier family rule for a task-dir verifier (0195-runner-family-task-dir)
  - T-0196 Step state for a whole-ticket (batched) verifier result (0196-batch-state)
  - T-0197 steps.py lane, review_required(), and skips.md (0197-lane)
  - T-0198 skips.md guard in tickets.py check and close (0198-skips-guard)
  - T-0199 Conductor batching and skip rules (0199-conductor-rules)
  - T-0200 Replan by delta: merged plan view and steps.py resolve (0200-plan-merge)
  - T-0201 Anchor rule for step blocks and its lint check (0201-anchor)
  - T-0202 Carry forward section in scout, researcher, architect, archaeologist (0202-carry-forward)
  - T-0203 fanout.py merge-time file-overlap check (0203-fanout-overlap)
  - T-0204 fanout.py resolves lane tickets through ticket_dir (0204-fanout-resolver)
  - T-0205 layout key and one resolver for ticket dir, roadmap, notes (0205-layout-resolver)
  - T-0206 tickets.py migrate-layout (0206-migrate-layout)
  - T-0207 Readers and docs for the topic layout (0207-layout-readers-docs)
  - T-0208 Live evidence: lean and full ticket on both hosts (0208-live-evidence)
- ready: 5
  - T-0183 supervisor.py: deterministic watcher that resumes an idle host on new mail (0183-supervisor-script)
  - T-0184 One declared result schema per role, validated before the next role reads it (0184-role-result-schema)
  - T-0185 evals/ folder, evals.py, and a model-table change must cite an eval (0185-evals-folder)
  - T-0186 proposals/ folder and proposals.py mining runs and notes for candidate changes (0186-proposals-folder)
  - T-0187 board.py --overview: queue, running roles, supervisor, unread mail from the folders (0187-board-overview)
- blocked: 0
- done: 168
- dropped: 19

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

<!-- sdlc-lite:managed:start v1 sha256:512bc8726363 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 6
  - T-0301 Conductor schedules the rerun after a 429 limit (0301-limit-conductor-rerun)
  - T-0316 Live headless chain run on Codex, recorded (0316-codex-live-evidence)
  - T-0317 Verifier policy: a browser-test red under measured load re-runs once alone before it counts (0317-red-under-load-rerun)
  - T-0381 Native runner accepts a valid ancestor that is the wrong lane base (0381-runner-wrong-lane-base)
  - T-0385 Rebase the Codex lean-template hunks onto 0.22.x and answer per hunk (0385-template-hunks-0301)
  - T-0410 Plan-doc contract, plan_done.py and a run-plan executor any builder tier can drive with /goal (0410-plan-doc-executor-design)
- ready: 9
  - T-0411 Collector fields for K-002, K-003, K-004 and verifier minutes (0411-collector-fields-k002-k004), claimed by claude 2026-10-09
  - T-0412 record leaves the attempt running when no result exists yet (0412-record-before-result-file), claimed by claude 2026-10-09
  - T-0413 prepare --tree names the lane worktree as Tree and base (0413-prepare-tree-lane-worktree)
  - T-0414 Restart sweep, reused parent pids, and a safe prune --add (0414-restart-sweep-and-safe-prune)
  - T-0415 Lint refuses circular criteria and records every refusal (0415-lint-circular-criteria), claimed by claude 2026-10-09
  - T-0416 Replay a scope-versus-tests heuristic and decide (0416-scope-vs-tests-heuristic-replay)
  - T-0417 Measure verifier minutes and decide on a delta verifier (0417-verifier-minutes-delta-decision)
  - T-0418 Replay solo-sized chunks on ultimate-tokens T-0040 and T-0044 to size the full-chain cost on L4 (0418-l4-full-chain-cost-replay)
  - T-0419 Write the standing narrow authorization for managed-block refresh in consumer repos (0419-standing-managed-block-auth), claimed by claude 2026-10-09
- blocked: 0
- done: 372
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

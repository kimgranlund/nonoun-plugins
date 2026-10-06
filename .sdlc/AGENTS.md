<!-- sdlc-lite:managed:start v1 sha256:81a9ba1f5142 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 44
  - T-0205 layout key and one resolver for ticket dir, roadmap, notes (0205-layout-resolver)
  - T-0206 tickets.py migrate-layout (0206-migrate-layout)
  - T-0207 Readers and docs for the topic layout (0207-layout-readers-docs)
  - T-0233 Gated apply for an approved reorganization plan (dry run, citing-file scan, commit per batch, restore) (0233-reorg-apply)
  - T-0244 Migrate this repository's docs/ to the schema through the reorganization tooling (0244-docs-schema-migration)
  - T-0245 Promotion helper: copy a .sdlc artifact into a docs home with source front matter (0245-docs-promotion-helper)
  - T-0248 Placement proof for the context registry (0248-placement-proof)
  - T-0252 Record which context a run loaded (0252-pc-run-context-trace)
  - T-0253 Entry-file resolver in onboard.py check (0253-pc-entry-file-resolver)
  - T-0254 Handoff and evidence lints with citation resolver (0254-pc-evidence-lints)
  - T-0264 steps.py split has no override after a replan verdict (0264-split-after-replan-override)
  - T-0265 Headless planner stalled on a denied rm permission prompt (0265-headless-planner-denied-rm)
  - T-0266 tickets.py check breaks on partial front matter (0266-tickets-check-partial-front-matter)
  - T-0267 A hook denies git worktree add with variable paths (0267-hook-denies-worktree-add-variable)
  - T-0268 Raw claude -p solos have no solo_run cost records (0268-raw-solo-cost-records)
  - T-0269 traces detector reports failed attempts as missing a runs.jsonl row (0269-traces-failed-attempt-noise)
  - T-0270 steps.py lint gives a generic error for nested backticks (0270-steps-lint-nested-backtick-message)
  - T-0271 steps.py lint should enforce plan-defect contract dependents (0271-planner-contract-dependents-lint)
  - T-0272 Conductor honors a repo opt-out of delegation (0272-conductor-repo-opt-out)
  - T-0275 Probe the sub-agent mechanics the design assumes (0275-subagent-probes)
  - T-0276 Claude level table and per-level generated agents (0276-claude-levels-table)
  - T-0277 dispatch.py prepare: the pre-launch half of run.sh (0277-dispatch-prepare)
  - T-0278 dispatch.py record: validate, record, and close a dispatched role (0278-dispatch-record)
  - T-0279 dispatch.py status and resume for dead or interrupted sub-agents (0279-dispatch-recover)
  - T-0280 Estimated cost for sub-agent runs from tokens and a price table (0280-cost-estimate)
  - T-0281 Hooks key on agent_type; spawn gate replaces block-role-spawn (0281-hooks-agent-role)
  - T-0282 Conductor and chain dispatch roles as sub-agents (0282-conductor-dispatch-core)
  - T-0283 Launcher skills dispatch through sub-agents (0283-launcher-skills-dispatch)
  - T-0284 Solo and its verifier run as sub-agents (0284-solo-subagent)
  - T-0285 Fanout lanes as isolated background sub-agents (0285-fanout-subagent)
  - T-0286 Supervisor reports orphaned dispatches (0286-supervisor-orphans)
  - T-0287 Live evidence for sub-agent mode, including an account switch (0287-subagent-live-evidence)
  - T-0288 Retire the Claude headless execution path (0288-retire-claude-exec)
  - T-0292 Machine-wide gate semaphore so a load stop line counts gates, not lanes (0292-machine-wide-gate-semaphore)
  - T-0301 Conductor schedules the rerun after a 429 limit (0301-limit-conductor-rerun)
  - T-0302 ADR number allocator note (repo-owned, docs only) (0302-adr-number-allocator-note)
  - T-0307 fleet-retro interview template and environment fingerprint (0307-fleet-interview)
  - T-0308 /sdlc-lite:fleet-retro skill, cross-repo report, verification sample (0308-fleet-retro-skill)
  - T-0311 fleet_status.py: liveness join, load trend and snapshot (0311-fleet-liveness)
  - T-0312 fleet_status.py render and the /sdlc-lite:fleet-status skill (0312-fleet-status-render)
  - T-0313 solo role blocked by block-stray-worktree: conductor must create the lane worktree and branch first (0313-solo-worktree-hook)
  - T-0314 Red-first control: a (red) criterion must fail at base and pass after, for solo and chain (0314-red-first-control)
  - T-0315 Re-measure planner and replan cost after T-0297 and the L4/L5 plan-review rule (0315-replan-cost-remeasure)
  - T-0316 Live headless chain run on Codex, recorded (0316-codex-live-evidence)
- ready: 0
- blocked: 0
- done: 240
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

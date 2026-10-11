<!-- sdlc-lite:managed:start v1 sha256:dfeac66da034 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 14
  - T-0301 Conductor schedules the rerun after a 429 limit (0301-limit-conductor-rerun)
  - T-0316 Live headless chain run on Codex, recorded (0316-codex-live-evidence)
  - T-0317 Verifier policy: a browser-test red under measured load re-runs once alone before it counts (0317-red-under-load-rerun)
  - T-0381 Native runner accepts a valid ancestor that is the wrong lane base (0381-runner-wrong-lane-base)
  - T-0385 Rebase the Codex lean-template hunks onto 0.22.x and answer per hunk (0385-template-hunks-0301)
  - T-0424 Add the git-native conventions to the lane lifecycle design: names, archive refs, worktree lock, worktree config (0424-lane-lifecycle-git-native)
  - T-0427 Design a cascade guard: a per-ticket agent-run counter that stops and asks, and a template-instance plan review (0427-cascade-guard-design)
  - T-0442 Replay A/B of builder overlays on the five bench tasks (0442-builder-overlay-ab)
  - T-0443 Extend overlays to the other roles and levels, gated on the A/B (0443-overlays-other-roles)
  - T-0445 Collector and recover: a completed attempt is never counted or marked interrupted (0445-collector-ignores-completed-attempts)
  - T-0446 dispatch.py record finds the sub-agent transcript without a flag (0446-record-finds-transcript)
  - T-0447 Document standards: registry, core rules, six family cards, schemas, templates, glossary, checks, and pointers (0447-doc-standards-suite)
  - T-0448 Modernize clarify (our port of find-intent): plan-ready intent, runnable done-when, cost-aware asks (0448-clarify-v2-intent-to-plan)
  - T-0449 Committed solo lane stats script and a KPI with a baseline (0449-solo-campaign-stats)
- ready: 0
- claimed: 0
- paused: 0
- blocked: 0
- done: 403
- dropped: 25

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
2. Set `status: claimed` and add `claimed_by: <claude|codex> <YYYY-MM-DD>` to the front matter, then run `python3 <plugin-root>/scripts/tickets.py --root .sdlc roadmap`.
3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> .sdlc/<folder>/handoff.md`, or `/sdlc-lite:chain .sdlc/<folder>`. Progress shows on `/board`.
4. Release: remove the `claimed_by:` line and set `status: ready`. Pause: set `status: paused` and add a one-line `paused_reason:`. Rerun `roadmap` after either.

Close a ticket:
1. Run the filer (`/file`): `<plugin-root>/scripts/run.sh filer L1 .sdlc/<folder>/handoff.md`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run`. It lists each follow-up as `<i>. <tag>: <title>` and ends with `expect <digest>`.
3. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder>`. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `notes.md`; `fix-now:` items are finished before the close.
4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --reason "<why>"`.
<!-- sdlc-lite:managed:end -->

## Other records

- Evals: `evals/` holds the dated model and effort experiments and `table-lock.json`; read `evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
- Proposals: `proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.

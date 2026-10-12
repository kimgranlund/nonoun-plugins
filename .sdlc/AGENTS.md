<<<<<<< HEAD
<!-- sdlc-lite:managed:start v1 sha256:07e9d14f3f85 -->
=======
<!-- sdlc-lite:managed:start v1 sha256:f74b94cf7dcc -->
>>>>>>> fanout/wave49
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

<<<<<<< HEAD
- proposed: 19
=======
- proposed: 8
>>>>>>> fanout/wave49
  - T-0463 Standardize skill argument hints and question UI across all skills, with a parity lint (0463-skill-ui-hints)
  - T-0465 /plan compaction <prose>: a kind of the plan skill that authors one /compact prompt (from the ultimate-tokens handoff) (0465-compaction-prompt)
  - T-0467 Merge plan skills A: new /plan skill with kinds steps, doc, goal, campaign, fanout (0467-plan-merge-a-skill)
  - T-0468 Merge plan skills B: redirect stubs for the four retired names and retargeted checks (0468-plan-merge-b-stubs)
  - T-0469 Merge plan skills C: plan_check --summary cost line and controlled-language rules (0469-plan-merge-c-summary)
<<<<<<< HEAD
  - T-0487 loaded_context shows rollout absent on codex exec runs (0487-codex-exec-rollout-absent)
  - T-0494 A role that spawns background sub-agents then ends its turn never wakes: completion notices go to the parent session (T-0493) (0494-subagent-notice-routing)
=======
  - T-0492 Merge ops duty block in conductor.md, fanout skill steps 4 and 5, and a recipe in run-operations.md (T-0488) (0492-merge-ops-duty-block)
>>>>>>> fanout/wave49
  - T-0496 Pilot: solo L2 closes on green criteria with observed-red controls; verifier by exception (0496-tests-gate-pilot)
  - T-0500 agents/solo.md: regenerate derived files and scan em dashes and stale counts before verify (retro 12h rows 7 and 8) (0500-solo-brief-regenerate-scan)
  - T-0502 lanes.py: a new lane worktree gets the gitignored .claude/settings.local.json (agent-ui retro row 7) (0502-lane-copies-local-settings)
  - T-0510 profile: inner-loop, local_gate and full_gate in .sdlc/config: solo_run refuses a full-suite criterion (T-0501 B1) (0510-inner-loop-b1-config)
  - T-0511 verifier: a Notes section for nits, carried into the close reason (T-0501 B2) (0511-inner-loop-b2-notes)
  - T-0512 steps.py lane routes L3 to solo under the inner-loop profile (T-0501 B3) (0512-inner-loop-b3-l3-solo)
  - T-0513 A (parity) criterion for styling tickets: screenshot pair with named properties (T-0501 B4) (0513-inner-loop-b4-parity)
  - T-0514 dispatch.py resume accepts a running attempt whose transcript is silent (T-0501 B5) (0514-inner-loop-b5-resume-silent)
  - T-0515 Merge ops names the two PR merge invariants; fanout skill and run-operations (T-0501 B6) (0515-inner-loop-b6-merge-contract)
- ready: 7
  - T-0503 bug: Claude agents: serialize valid YAML descriptions (0503-claude-agent-frontmatter)
  - T-0504 bug: Claude dispatch: preserve handoff paths containing spaces (0504-claude-dispatch-space-paths)
  - T-0505 bug: Claude hooks: freeze handoffs during prepared attempts (0505-claude-prepared-handoff-freeze)
  - T-0506 bug: Codex profiles: reconcile fingerprint and report contracts (0506-codex-profile-output-envelope)
  - T-0507 bug: Codex exchange: enforce the dispatched profile binding (0507-codex-exchange-fingerprint-binding)
  - T-0508 bug: ask: discover blockers in every supported ticket layout (0508-ask-ticket-layout-sweep)
  - T-0509 chore: guidance: align recovery behavior and Codex agent counts (0509-operator-recovery-agent-inventory)
- claimed: 0
- paused: 0
- blocked: 0
<<<<<<< HEAD
- done: 453
=======
- done: 456
>>>>>>> fanout/wave49
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

<!-- sdlc-lite:managed:start v1 sha256:2b2ab2b7fb94 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 6
  - T-0463 Standardize skill argument hints and question UI across all skills, with a parity lint (0463-skill-ui-hints)
  - T-0465 /plan compaction <prose>: a kind of the plan skill that authors one /compact prompt (from the ultimate-tokens handoff) (0465-compaction-prompt)
  - T-0468 Merge plan skills B: redirect stubs for the four retired names and retargeted checks (0468-plan-merge-b-stubs)
  - T-0469 Merge plan skills C: plan_check --summary cost line and controlled-language rules (0469-plan-merge-c-summary)
  - T-0512 steps.py lane routes L3 to solo under the inner-loop profile (T-0501 B3) (0512-inner-loop-b3-l3-solo)
  - T-0513 A (parity) criterion for styling tickets: screenshot pair with named properties (T-0501 B4) (0513-inner-loop-b4-parity)
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
- done: 466
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

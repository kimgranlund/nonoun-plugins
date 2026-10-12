<!-- sdlc-lite:managed:start v1 sha256:5024bf83a1b4 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 17
  - T-0301 Conductor schedules the rerun after a 429 limit (0301-limit-conductor-rerun)
  - T-0316 Live headless chain run on Codex, recorded (0316-codex-live-evidence)
  - T-0317 Verifier policy: a browser-test red under measured load re-runs once alone before it counts (0317-red-under-load-rerun)
  - T-0381 Native runner accepts a valid ancestor that is the wrong lane base (0381-runner-wrong-lane-base)
  - T-0385 Rebase the Codex lean-template hunks onto 0.22.x and answer per hunk (0385-template-hunks-0301)
  - T-0443 Extend overlays to the other roles and levels, gated on the A/B (0443-overlays-other-roles)
  - T-0455 fanout prep and run-plan rules set status: claimed with claimed_by (0455-fanout-claimed-status)
  - T-0456 Cheap fanout gates time out in the machine-wide gate lock behind heavy browser jobs (0456-cheap-gates-queue-behind-heavy)
  - T-0458 Retest the builder overlays on tasks where builders actually block, plus one L5 pair (0458-builder-overlay-retest)
  - T-0459 gate_lock selftest isolation case fails when other sessions use the real gate-lock state (0459-gate-lock-selftest-real-root-flake)
  - T-0460 Build /sdlc-lite:report: scripts/report.py and the skill (executive summary, views, health signals, hygiene grade) (0460-report-skill)
  - T-0461 Apply the controlled language system to /clarify: prompt, question wording, handoff grammar, lint rules, evals (0461-clarify-controlled-language)
  - T-0462 Design: merge the plan-* skills into /plan with kinds, shared rules and one lint (0462-plan-skills-merge-design)
  - T-0463 Standardize skill argument hints and question UI across all skills, with a parity lint (0463-skill-ui-hints)
  - T-0464 Audit ceremony versus defects caught; rank candidate changes toward a resolve-and-ship posture (0464-ceremony-audit)
  - T-0465 /plan compaction <prose>: a kind of the plan skill that authors one /compact prompt (from the ultimate-tokens handoff) (0465-compaction-prompt)
  - T-0466 reply_lint.py: score assistant replies against the author output rules, and run the 3-arm comparison (0466-reply-lint)
- ready: 0
- claimed: 0
- paused: 0
- blocked: 0
- done: 417
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

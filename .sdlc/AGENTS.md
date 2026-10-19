<!-- sdlc-lite:managed:start v1 sha256:353a378bef16 -->
# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: next to this file.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

## Stages

- proposed: 3
  - T-0577 --rewrite-refs rewrites citations inside frozen records (0577-rewrite-refs-frozen-paths)
  - T-0583 Driver loop wakes on role completion or state change, not timed polling (0583-event-driven-driver)
  - T-0584 tickets.py inventory: landed state by content and patch identity (0584-tickets-inventory)
- ready: 18
  - T-0611 Rehearse a Pi host working tickets beside Claude and Codex (0611-pi-host-rehearsal)
  - T-0619 docs_check: every doc listed in its home index, per-home file cap (0619-docs-index-and-cap)
  - T-0620 docs: generated folder index, opt-in numbering with atomic allocation, declared UPPERCASE singletons (0620-docs-uppercase-masters)
  - T-0622 work_root t02: records base: one state_of rule for order.py, records.sh, steps.py, budget.py, dispatch.py (0622-work-root-t02-records-base-one-state-of-rule-for-order)
  - T-0623 work_root t03: tickets.py resolution sites: new/claim/roadmap/check/tidy in the work root (ROADMAP.md, NO (0623-work-root-t03-tickets-py-resolution-sites-new-claim-ro)
  - T-0624 work_root t04: tickets.py close/number/archive: dot rename and citation scan under the work root (0624-work-root-t04-tickets-py-close-number-archive-dot-rena)
  - T-0625 work_root t05: generated router .sdlc/AGENTS.md names work-root paths; work-root entry file; onboard root (0625-work-root-t05-generated-router-sdlc-agents-md-names-wo)
  - T-0626 work_root t06: lanes and fanout: untracked work-root tickets are trail, not dirt; generated work-root fil (0626-work-root-t06-lanes-and-fanout-untracked-work-root-tic)
  - T-0627 work_root t07: record-prefix consumers: verify_scope size/protected gates, reorg freeze and digest, inven (0627-work-root-t07-record-prefix-consumers-verify-scope-siz)
  - T-0628 work_root t08a: ticket and run readers: fleet_collect keys, solo_stats, report, board (0628-work-root-t08a-ticket-and-run-readers-fleet-collect-key)
  - T-0629 work_root t08b: fleet registry and notes readers: fleet_config, fleet_status, fleet_doctor (0629-work-root-t08b-fleet-registry-and-notes-readers-fleet-c)
  - T-0630 work_root t09a: evals, proposals, promote read and write the work root (0630-work-root-t09a-evals-proposals-promote-read-and-write-t)
  - T-0631 work_root t09b: plan_check, plan_done, solo_run: notes-path rule and new plain task folder from the resolv (0631-work-root-t09b-plan-check-plan-done-solo-run-notes-path)
  - T-0632 work_root t10: check.py reads record paths from the resolver: NAME_ALLOW and the evals lock path (0632-work-root-t10-check-py-reads-record-paths-from-the-res)
  - T-0633 work_root t11: agent and skill prose names record paths layout-neutrally; regenerate Claude level agents (0633-work-root-t11-agent-and-skill-prose-names-record-paths)
  - T-0634 work_root t14: work/ is a first-class docs home: onboard templates for the docs/AGENTS.md block row and t (0634-work-root-t14-work-is-a-first-class-docs-home-onboard)
  - T-0635 work_root t12: tickets.py migrate-work-root: flat, nested and topics sources into one docs/work shape (0635-work-root-t12-tickets-py-migrate-work-root-flat-nested)
  - T-0636 work_root t13: migrate this repository to docs/work (0636-work-root-t13-migrate-this-repository-to-docs-work)
- claimed: 0
- paused: 0
- blocked: 0
- done: 579
- dropped: 29

## Procedures

Folder layout:
- The top of `.sdlc` holds only ticket and task folders (a folder with a `handoff.md` or `plan-doc.md`), `AGENTS.md`, `CLAUDE.md`, `config`, `roadmap.md`, `board.md`, `notes.md`, `notes/`, `fleet.json`, `gate-ledger.jsonl`, `messages/`, `runtime/`, `supervisor/`, `evals/`, `proposals/`, `goals/`, `tickets/`, `work/`, `archive/`, and `_`- or `.`-prefixed entries. A `top_level_allow: <glob>, ...` line in `.sdlc/config` allows more.
- Run records (role results, attempts, `runs.jsonl`, `skips.md`) go in the git-ignored records dir `.sdlc/runtime/tasks/<folder>/` (`<plugin-root>/scripts/order.py records-dir .sdlc/<folder>` prints it). Notes go to `notes.md`, an answer to another agent goes by `messages.py send`, anything else into `archive/`.
- `python3 <plugin-root>/scripts/tickets.py --root .sdlc check` warns on any other top-level entry; `python3 <plugin-root>/scripts/tickets.py --root .sdlc tidy` lists its move into `archive/` and `python3 <plugin-root>/scripts/tickets.py --root .sdlc tidy --apply` makes it. Move nothing under `.sdlc` while a `*.running` marker exists: a role is using it.

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
3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> .sdlc/<folder>/handoff.md`, or `/sdlc-lite:chain .sdlc/<folder>`. Progress shows on `/board`.
4. Release: `python3 <plugin-root>/scripts/tickets.py --root .sdlc release <id>`. Pause: set `status: paused` and add a one-line `paused_reason:`, then rerun `roadmap`.

Open a lane:
1. Claim the ticket first: `<plugin-root>/scripts/lanes.py open` refuses an unclaimed local ticket.
2. Run `python3 <plugin-root>/scripts/lanes.py open <name> --kind solo --ticket <id>`. It makes the worktree and branch under the worktree root (`../<repo>.worktrees/`) and writes `branch: <lane branch>` and `worktree: <path>` after `claimed_by:`, so verified, unmerged work stays visible on the roadmap and in `lanes.py list --all`. A worktree made by hand: run `python3 <plugin-root>/scripts/tickets.py --root .sdlc branch <id> <branch> --worktree <path>`.
3. `lanes.py close <name>` removes the `branch:` and `worktree:` lines once the lane closes.

Close a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run`. It checks the verifier verdict, lists each verifier `## Notes` line as `<i>. <tag>: <title>`, and ends with `expect <digest>`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --changed "<one line>"`. It appends `## Outcome` to the handoff. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `notes.md`; `fix-now:` items are finished before the close. When it refuses because files cite the folder, add `--rewrite-refs` to rewrite them to the closed `.<folder>` path.
3. Only when a filer draft was asked for (`/file`): `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --filer`.
4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --reason "<why>"`.

Ticket lifecycle:
1. Pick and claim: `python3 <plugin-root>/scripts/tickets.py --root .sdlc claim <id> --by <agent>`.
2. Lane: `python3 <plugin-root>/scripts/steps.py lane .sdlc/<folder>` prints the lane.
3. Build: the solo agent, `/sdlc-lite:fix`, or `/sdlc-lite:chain .sdlc/<folder>`.
4. Verify: one independent verifier per ticket (`/sdlc-lite:verify`).
5. Land: `python3 <plugin-root>/scripts/fanout.py land <branch>` for a lane branch, else merge the branch.
6. Close: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --changed "<one line>"`, as in Close a ticket above.
<!-- sdlc-lite:managed:end -->

## Other records

- Evals: `evals/` holds the dated model and effort experiments and `table-lock.json`; read `evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
- Proposals: `proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.

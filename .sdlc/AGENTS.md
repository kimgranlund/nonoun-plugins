<!-- sdlc-lite:managed:start v1 sha256:65c12ea650c0 -->
# Work records

This folder holds SDLC Lite `config`, this router, and the git-ignored `runtime/` and `messages/`. Tickets, task records, `docs/work/ROADMAP.md`, and `docs/work/NOTES.md` are in the work root `docs/work/`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `docs/work/ROADMAP.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

- Ticket folders: `docs/work/`, the work root `work_root:` in `.sdlc/config` names.
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
- `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.
- No plugin installed: follow `.sdlc/by-hand.md` to create, claim, release or close a ticket with git alone.

## Stages

- proposed: 18
  - T-0646 Every role writes its result file and ends with a one-line pointer (docs/work/0646-role-result-pointer)
  - T-0648 prepare appends the repo skills for a step's file scope (docs/work/0648-prepare-repo-skills)
  - T-0652 Outcome gains an optional Lessons line (docs/work/0652-outcome-lessons-line)
  - T-0653 Roadmap renders an Open follow-ups section from NOTES.md (docs/work/0653-roadmap-open-followups)
  - T-0654 fanout.py sync brings a lane up to date with the integration branch (docs/work/0654-fanout-sync-lane)
  - T-0655 prepare checks lane guidance against main and named guidance paths (docs/work/0655-lane-guidance-check)
  - T-0656 settle --forward refuses while a lane attempt is running (docs/work/0656-settle-refuses-running)
  - T-0657 steps.py review reports red criteria already green at base (docs/work/0657-review-red-at-base)
  - T-0659 Every SKILL.md stays under 18,000 characters (docs/work/0659-skill-size-limit)
  - T-0661 Verifier brief carries a base..end diff range per built step (docs/work/0661-verifier-diff-range)
  - T-0662 Tracked work records hold no absolute machine paths (docs/work/0662-relative-record-paths)
  - T-0665 Drop redirect stub skills and shorten level-variant agent descriptions (docs/work/0665-trim-skill-catalog)
  - T-0666 Plan lint rejects git stash and --autostash in Do text (docs/work/0666-lint-git-stash)
  - T-0667 record --agent-id reads the final message from the transcript (docs/work/0667-record-agent-id)
  - T-0668 ui-designer reads SKILL.md first and opens references by cue (docs/work/0668-ui-designer-progressive)
  - T-0669 Dispatch and skip records go to the records dir, not the work root (docs/work/0669-dispatch-records-dir)
  - T-0670 close verdict reason matches the recorded lane (docs/work/0670-close-lane-reason)
  - T-0671 onboard entry text agrees with the docs table on where plans go (docs/work/0671-onboard-plans-wording)
- ready: 1
  - T-0611 Rehearse a Pi host working tickets beside Claude and Codex (docs/work/0611-pi-host-rehearsal)
- claimed: 3
  - T-0645 dispatch.py advance runs record, prune, next and prepare in one call (docs/work/0645-dispatch-advance), claimed by sdlc-lite-author 2026-10-20
  - T-0651 A reason close routes follow-ups like a verified close (docs/work/0651-reason-close-followups), claimed by sdlc-lite-author 2026-10-20
  - T-0660 Plan lint flags universally quantified prose criteria with no command (docs/work/0660-quantified-criteria-lint), claimed by sdlc-lite-author 2026-10-20
- paused: 0
- blocked: 0
- done: 614
- dropped: 29

## Procedures

Folder layout:
- The top of `.sdlc` holds only `AGENTS.md`, `CLAUDE.md`, `by-hand.md`, `config`, `board.md`, `fleet.json`, `gate-ledger.jsonl`, `messages/`, `runtime/`, `supervisor/`, `evals/`, `proposals/`, `goals/`, `tickets/`, `work/`, `archive/`, and `_`- or `.`-prefixed entries; ticket and task folders go in `docs/work/`. A `top_level_allow: <glob>, ...` line in `.sdlc/config` allows more.
- Run records (role results, attempts, `runs.jsonl`, `skips.md`) go in the git-ignored records dir `.sdlc/runtime/tasks/<folder>/` (`<plugin-root>/scripts/order.py records-dir docs/work/<folder>` prints it). Notes go to `docs/work/NOTES.md`, an answer to another agent goes by `messages.py send`, anything else into `../docs/work/archive/`.
- `python3 <plugin-root>/scripts/tickets.py --root .sdlc check` warns on any other top-level entry; `python3 <plugin-root>/scripts/tickets.py --root .sdlc tidy` lists its move into `../docs/work/archive/` and `python3 <plugin-root>/scripts/tickets.py --root .sdlc tidy --apply` makes it. Move nothing under `.sdlc` while a `*.running` marker exists: a role is using it.

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
3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> docs/work/<folder>/handoff.md`, or `/sdlc-lite:chain docs/work/<folder>`. Progress shows on `/board`.
4. Release: `python3 <plugin-root>/scripts/tickets.py --root .sdlc release <id>`. Pause: set `status: paused` and add a one-line `paused_reason:`, then rerun `roadmap`.

Open a lane:
1. Claim the ticket first: `<plugin-root>/scripts/lanes.py open` refuses an unclaimed local ticket.
2. Run `python3 <plugin-root>/scripts/lanes.py open <name> --kind solo --ticket <id>`. It makes the worktree and branch under the worktree root (`../<repo>.worktrees/`) and writes `branch: <lane branch>` and `worktree: <path>` after `claimed_by:`, so verified, unmerged work stays visible on the roadmap and in `lanes.py list --all`. A worktree made by hand: run `python3 <plugin-root>/scripts/tickets.py --root .sdlc branch <id> <branch> --worktree <path>`.
3. `lanes.py close <name>` removes the `branch:` and `worktree:` lines once the lane closes.

Close a ticket:
1. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run`. It checks the verifier verdict, lists each verifier `## Notes` line as `<i>. <tag>: <title>`, and ends with `expect <digest>`.
2. Run `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --changed "<one line>"`. It appends `## Outcome` to the handoff. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `docs/work/NOTES.md`; `fix-now:` items are finished before the close. When it refuses because files cite the folder, add `--rewrite-refs` to rewrite them to the closed `.<folder>` path.
3. Only when a filer draft was asked for (`/file`): `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --filer`.
4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --reason "<why>"`.

Ticket lifecycle:
1. Pick and claim: `python3 <plugin-root>/scripts/tickets.py --root .sdlc claim <id> --by <agent>`.
2. Lane: `python3 <plugin-root>/scripts/steps.py lane docs/work/<folder>` prints the lane.
3. Build: the solo agent, `/sdlc-lite:fix`, or `/sdlc-lite:chain docs/work/<folder>`.
4. Verify: one independent verifier per ticket (`/sdlc-lite:verify`).
5. Land: `python3 <plugin-root>/scripts/fanout.py land <branch>` for a lane branch, else merge the branch.
6. Close: `python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --changed "<one line>"`, as in Close a ticket above.
<!-- sdlc-lite:managed:end -->

## Other records

- Evals: `../docs/work/evals/` holds the dated model and effort experiments and `table-lock.json`; read `../docs/work/evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
- Proposals: `../docs/work/proposals/` holds candidate changes that `proposals.py scan` mined from past runs; read `../docs/work/proposals/AGENTS.md` before scanning, accepting, rejecting, or promoting one.

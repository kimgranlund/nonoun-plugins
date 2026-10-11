# Run rules

The driver's procedure. Every pass starts from the files, never from memory; nothing you hold is load-bearing, so a restart costs only the step in flight. `PD` below is the plan doc path and `SCRIPTS` is `${CLAUDE_PLUGIN_ROOT}/scripts`.

## Routing table

| Signal | You do |
|---|---|
| `plan_done.py` exit 0 (last line `plan done`) | Stop and report. Set nothing; the records already say done |
| exit 4 (`stopped: ...; resume: ...`) | Stop and report the line. The state is already written. The stop record is sticky: once its cause is fixed, `python3 SCRIPTS/plan_done.py resume PD` (the `resume:` command the line prints) clears it and the loop continues; never `rm` `plan-state.json` |
| exit 2 (`plan defect: <rule>`) | `plan_done.py stop PD --reason "plan defect: <rule>"`, then end |
| exit 1 | Take the first open item (the lines before the last, in step order) |
| `dispatch.py prepare` or `fanout.py prep` exit 2, 4 or 5 | Stop with the printed words as the reason (a refusal, a budget stop at 80 percent, the solo-lane gate). Never run `budget.py ack` |
| `steps.py next` prints a stop, a plan defect, or `recurring` | One replan: `plan_done.py replan PD --reason R`, then dispatch the planner as printed by `dispatch.py prepare planner L3`. The second `replan` call refuses and stops the run |
| A merge conflict, an inherited red, a limit (rate, weekly, three 529s in a row) | `plan_done.py stop` with the words, then end |
| A command outside the plan's Authorization (push, tag, publish, `onboard.py setup`, an external write) | Do not run it. `plan_done.py stop` with the command as the reason |

## Preflight, once per session

1. `python3 SCRIPTS/plan_check.py plan --file PD --run` exits 0. A non-zero exit is a stop.
2. `python3 SCRIPTS/tickets.py --root .sdlc check` exits 0.
3. For each step folder that already exists: `python3 SCRIPTS/dispatch.py recover <folder>` then `dispatch.py status <folder>`. An attempt marked interrupted is re-dispatched with a fresh `prepare`; a live agent is resumed with `SendMessage` by name first, then `prepare`. When `dispatch.py recover --root .` exists in this plugin version, run it once instead of the per-folder form, always as `dispatch.py recover --root . --open`: the bare form also rewrites the attempt files of every closed ticket and dirties the checkout.
4. Print the front matter `driver:` and the model you are running; warn when they differ. Say the plan's Authorization in one line.
5. Run `git rev-parse --show-toplevel`. If it is not the repository that holds the plan doc, stop with state written: the host makes sub-agent worktrees from the session's repository.

## The loop

1. `python3 SCRIPTS/plan_done.py PD`. Print its output unchanged at every step boundary: the stop hook reads it from the transcript. Branch on the table above.
2. Step prep for the first open step, in this order:
   - `ticket: new <type> <slug>`: run `python3 SCRIPTS/tickets.py --root .sdlc new <type> <slug> "<step title>"`, then copy the step's Do and Acceptance criteria into the new handoff once and set its front matter `size:` to the step's `level` and `status: ready` (the template defaults to `size: L2` and `status: proposed`, and `steps.py lane` and `plan_done.py` read both). `verify` stays in the plan doc, which `plan_done.py` reads; do not copy it to the ticket. A handoff a role has read is frozen; never edit it.
   - An existing ticket: leave its handoff alone.
   - `python3 SCRIPTS/budget.py set --usd <cap number> <ticket folder>`.
   - Skip the claim when the handoff already holds `claimed_by`. Before `fanout.py prep`, look for an earlier attempt of this step: `git branch --list 'worktree-*'` and `git log --all --oneline --grep '^<ticket id>: '`. A lane branch whose last commit is `<ticket id>: <title>` is a finished solo: do not run `prep` or spawn again; continue at the verifier and `land` with that branch. A lane branch with only `WIP` commits is a stop with state written, never a rebuild.
   - Claim it (`claimed_by: claude <date>` in the handoff front matter, then `python3 SCRIPTS/tickets.py --root .sdlc roadmap`), then commit the ticket folder and roadmap on the current branch (`git add -- .sdlc` and a commit `<id>: claim`), because `fanout.py prep` refuses an uncommitted handoff. Never push.
   - `python3 SCRIPTS/steps.py lane <ticket folder>` and record `Lane: <lane> because <reason>` from its first line in the ticket folder's notes.
3. Dispatch with the existing path, one step at a time:
   - Lane `solo`: `python3 SCRIPTS/fanout.py prep <name>=<ticket id>` prints the dispatch JSON, the verifier command for L2 and L3, and the `land` command. Spawn the `Agent` tool with exactly the printed `subagent_type`, `name`, `description`, `model`, `prompt` and `isolation`, `run_in_background` as printed (false when `SDLC_HEADLESS=1`), never changed. One exception: when the host answers `Teammates cannot spawn other teammates` (a driver that is itself a named sub-agent), spawn again once without `name` and change nothing else; `name` is only a label, and `dispatch.py record` takes the agent id. Wait for its report in the same turn. The host names the lane branch `worktree-agent-<id>`, not the branch `prep` printed: find it with `git worktree list` and use it in the verifier and `land` commands, replacing only that branch name. Then run the verifier command exactly as printed (for a ticket of level L1 with `verify: required` prep prints none: get the level from `python3 SCRIPTS/steps.py verifier-level <ticket folder>` and run `dispatch.py prepare --tree <the sub-agent worktree> verifier <that level> <handoff path inside that worktree>`, spawn exactly the JSON it prints, and `record` it) and the `dispatch.py record` line it names; read `python3 SCRIPTS/steps.py next <step dir>` and follow it. Then run the printed `land` command; it merges, gates and closes on the integration branch that `prep` printed, not on your branch, and it first commits the verifier result and run records left in the sub-agent worktree's ticket folder onto the lane (`git add -f`, the ticket folder only), so the merge carries them in with no hand step. Close a step only through `land`: a hand merge or cherry-pick leaves the verifier result on the lane branch and `plan_done.py` reads `no independent verifier pass`. `plan_done.py` reads the tickets of the checkout it runs in, so bring the close back with `python3 SCRIPTS/fanout.py settle <integration branch that prep printed>` in the checkout the run started in (local only, never a push): it fast-forwards the checkout to the integration branch, removes the integration worktree and deletes the branch, so the next `prep` starts a new integration branch at the current tip. Exit 2 (not a fast-forward, or blocked by untracked files) is a stop; after a merge the maintainer made by hand, the same command only retires the branch.
   - Lane `full`: drive the chain workflow (`${CLAUDE_PLUGIN_ROOT}/skills/chain/SKILL.md`) against the lane tree; every later routing decision comes from `steps.py next`.
   - Independent steps with disjoint Upserts may run as parallel lanes, at most three; the default is one at a time.
4. Every decision after a role ends comes from `steps.py next` and from the `dispatch.py record` exit code. A verifier that died is dispatched again and is never counted as a fail (`steps.py next` prints `reverify`). A verifier `fail` goes back to solo once with the findings; a second fail is a stop. A solo that reports no diff possible because the step's (red) criterion already passes is a plan defect stop that names the commit that built it; the driver never closes that ticket itself.
5. After a step closes, run `python3 SCRIPTS/plan_done.py PD --records-only` as a cheap poll (it can never exit 0), then go to step 1.

## Records and what you never do

- Records are only what the scripts write: attempt records, `runs.jsonl`, results, `skips.md`, and `plan-state.json` through `plan_done.py stop` and `replan`. Hand-write no JSON and no verdict.
- You edit no product file. A ticket's change is made by the sub-agent the dispatch names, in its worktree.
- You never choose or change a verifier model or level; `dispatch.py prepare` keeps the verifier off the worker's family.
- You never ask a person and never call `AskUserQuestion`. A missing input is a stop with state written.
- You run no role in the background: a backgrounded role makes the driver look idle to the stop hook.
- A new idea becomes a new ticket, not a larger step; write it as one line to the notes file and move on.
- A recurring finding (the same criterion with the same root cause) is a replan of the plan, never a level bump.

## Resuming after a crash

Run the same `/goal` line. Preflight recovers orphaned attempts, `plan_done.py` shows what is still open, and the loop continues at the first open item. A step whose solo died has an interrupted attempt and a lane branch with WIP commits: `fanout.py prep` does not resume that branch (observed in the rehearsal: it printed a fresh dispatch and the host made a second worktree), so the loop's lane-branch check comes first and a finished branch is landed, never rebuilt.

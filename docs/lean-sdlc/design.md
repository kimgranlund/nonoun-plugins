# Lean SDLC design

Version 0.1, 2026-10-03. Proposal. Nothing here is built. Tickets T-0189, T-0190, T-0191, T-0192.

## Problem

A maintainer running SDLC Lite in another repo reported four things:

1. Planner, builder, and verifier granularity is excessive.
2. `.sdlc/` should always organize its contents in topic-specific sub-folders.
3. There are too many planning documents. The whole trace should not be written down, and a later step should not repeat research and planning already done.
4. The conductor should always look for the fastest efficient way to finish, including batching reviews.

These are one problem seen four ways: the system spends more roles, files, and tokens per ticket than the risk of the ticket justifies, and it stores the result in a flat folder that grows without a shape.

## Baseline (measured 2026-10-03)

Counted from `.sdlc/` artifacts and `runs.jsonl` of closed tickets on main. Bytes are file sizes of everything in the ticket folder; role runs are `runs.jsonl` lines.

| Ticket | Lane | Steps | Role runs | Files | Bytes (all) | Bytes (`.md`) |
| --- | --- | --- | --- | --- | --- | --- |
| T-0188 | /fix | 1 | 2 (builder L1, verifier L1) | 8 | 8,010 | 4,521 |
| T-0164 | /fix | 1 | 2 (builder L2, verifier L1) | 8 | 10,050 | 6,586 |
| T-0181 | /chain | 5 | 15 (planner 3, plan-reviewer 2, builder 5, verifier 5) | 51 | 214,502 | 185,323 |
| T-0175 | /chain | 8 | 21 (planner 1, plan-reviewer 1, builder 9, verifier 9, filer 1) | 69 | 224,330 | 187,209 |

What the numbers say:

- A chained ticket costs 22 to 27 times the bytes and 7 to 10 times the role runs of a /fix ticket. The fast lane already shows the floor: 2 role runs and 8 files.
- Roughly 3.3 files are written per role run (a result, an `attempt.json`, a `base-sha` or step handoff, and a shared `runs.jsonl`).
- Plans dominate the text. For T-0181 the three planner files total 105,542 bytes (22,152 for the L2 plan, then 33,296 and 50,094 for two L3 plans), about half of all `.md` bytes. The second L3 plan restated the whole plan to change part of it.
- A step handoff restates the plan. T-0181 step 1's handoff is 13,079 bytes, longer than the ticket handoff (8,333), because `steps.py split` copies the step block and the planner writes the settled decisions into it.
- Builder and verifier results are small (2,073 and 3,931 bytes for T-0181 step 1). The cost is the plan text and the number of processes, not the results.
- Contract text alone is 70,671 bytes across the conductor, planner, filer, builder, verifier, plan-reviewer, chain, fix, and handoff-format files, which every role start pays in part.

`footprint.py` (step A0 below) makes this measurement repeatable. These figures are the "before" for every target in this document.

## Principles

1. Process follows risk. The full chain is for work whose failure is expensive or cross-cutting. Everything else takes a shorter lane, and the choice is made by a script, not by prose.
2. Write a fact once. A later role reads the earlier result and the files it cites. It does not re-derive them and it does not get a new copy of them.
3. The folder system explains itself (as T-0175 to T-0179 did). A role that opens any folder learns the rules from that folder's `AGENTS.md`.
4. Independent verification is not a cost to trim. Lean means fewer, larger units of verification, never unverified work.
5. Every skip is recorded and every guard can fail. A skipped role leaves a line a check can find, and each new guard ships with a negative control.

## 1. Lean chain (T-0189)

Today the lanes are `/fix` (size S, no planner) and `/chain` (everything else). A size-M ticket pays for `/chain` in full. The change is a third lane between them and a planner rule that makes steps coarse.

### Lane selection

`steps.py lane <ticket dir>` (new) prints `fix`, `lean`, or `full` and the reasons, from facts the files already hold: ticket size, planner level, step levels, merge steps, files touched, and subsystem. The conductor runs it and follows the first line, the way it follows `steps.py next`.

| Lane | Use when | Roles |
| --- | --- | --- |
| fix | size S, one file's behavior, no plan needed (unchanged) | builder L1 or L2, verifier L1 |
| lean | size S or M, every condition in the lean list below holds | planner L2, builder and verifier per coarse step, one close-out |
| full | any condition in the mandatory list below | the current chain, unchanged |

### Lean conditions (all must hold)

- Planner level L1 or L2 (never the cross-cutting L3 plan).
- At most two steps, and every step at builder L1 to L3.
- No merge step and no replan.
- The change stays within one nearest `AGENTS.md` owner, or one script and its tests, with no change to a contract that other roles parse (role output sections, `run.sh` tables, `steps.py`, `tickets.py` invariants, hooks).

### Full chain is mandatory when any holds

- Planner L3, any step at builder L4 or L5, any merge step, or any replan. These are exactly the cases `steps.py review` already requires a plan review for (`steps.py` line 103), so the rule is not new and cannot drift from it.
- The ticket changes role behavior, a runner invariant, a hook, or a check. A focused live run is still required (plugin guidance), and lean does not waive it.
- A step that touches shared generated state (roadmap, router, generated Codex agents) alongside other tickets in flight.

### Coarse steps

The planner rule changes from "one step per file or concern" to "one step per independently verifiable outcome". A step may hold up to a stated number of criteria (proposed 12) including its guards. Two steps with a sequential dependency, the same builder level, and no intermediate gate merge into one. The plan's `gates green` final step (planner rule 14) stays the place for whole-suite gates, so a lean ticket is one or two steps plus the gates inside the last one.

`steps.py lint` gains a warning, not a refusal, when a lean-eligible plan has more than two steps or a step with one criterion, so the planner sees the rule without a hard failure.

### Verification and review in the lean lane

- Plan review: not required, because a lean plan is a routine plan under the existing rule. The conductor may still request one.
- One verifier per step, which is already one per two steps at most. A verifier never runs on the builder's family (`run.sh` enforces it), so independence is unchanged.
- Close-out: `tickets.py close --reason` with the verifier's result as evidence, as `/fix` does, unless the builder or verifier reported follow-ups or warnings. Then the filer runs. This keeps `close`'s existing refusal rule intact.

## 2. Single plan record (T-0191)

### Constraint

`run.sh`, `steps.py next`, and `order.py` read per-role result files by name (`builder-L*.md`, `verifier-L*.md`, newest wins). Replacing them with one appended file would rewrite the pipeline's decision core. So this design keeps the result files and removes the duplicated prose around them.

### Changes

1. **One plan file per ticket, revised by delta.** The planner writes `plan.md` once. A replan writes `plan-rev-<k>.md` holding only the changed or added steps and the findings it addresses, plus the unchanged step numbers by reference. `steps.py split` reads `plan.md` then applies revisions in order. Today a replan rewrites the whole plan (T-0181: 33,296 then 50,094 bytes). Target: a replan file at most a quarter of the plan it revises.
2. **Step handoffs by reference.** `split` writes each step handoff with the step block and a `### Read first` list, and replaces the restated plan context with one line naming `plan.md` and the settled-decision anchors the step cites. The builder reads the anchors, not a copy.
3. **An Understanding section, written once.** The scout, researcher, archaeologist, and architect each end their result with a short `## Carry forward` section (at most 15 lines: facts and paths that later roles must not re-derive). The planner copies none of it. It cites the result path. Later roles are told, in their contracts, to read `## Carry forward` before searching and to search only what it does not answer.
4. **What each role reads and writes.**

| Role | Reads | Writes |
| --- | --- | --- |
| scout, researcher, architect | ticket handoff | one result with `## Carry forward` |
| planner | ticket handoff, the `## Carry forward` sections | `plan.md` (or `plan-rev-<k>.md`) |
| plan-reviewer | ticket handoff, `plan.md` and revisions | one result |
| builder | its step handoff, the cited anchors in `plan.md`, its `### Read first` files | one result, with files changed |
| verifier | its step handoff and the builder result | one result |
| filer | the ticket handoff, results by name | one record |

5. **Handoff files stay the roles' only brief.** Nothing here widens what a role may read beyond what it cites. Progressive disclosure is the rule that keeps a role's context small.

### Targets

For a two-step ticket on the lean lane: at most 14 files and 60 KB of `.md`, against T-0181's 51 files and 185 KB. Planner text at most 20 KB. These are proposals until `footprint.py` measures a fixture ticket on both lanes.

## 3. Topic sub-folders as the default layout (T-0190)

### Target layout

```
.sdlc/
  AGENTS.md            router (entry file, as today)
  CLAUDE.md            @AGENTS.md
  config               layout and ticket settings
  tickets/             NNNN-slug/ per ticket, with its artifacts inside; .NNNN-slug/ when closed
    AGENTS.md  CLAUDE.md  roadmap.md
  work/                <slug>/ for tasks with no ticket (release records, verification handoffs, dogfood runs)
    AGENTS.md  CLAUDE.md
  messages/            new/ read/ done/ (T-0177 to T-0179, unchanged)
  notes/               notes.md and its entry file
  evals/  proposals/  supervisor/    from T-0183 to T-0187, each with its own entry file
  _templates/
```

Root holds only the router, its import, `config`, and `_templates/`. `roadmap.md` moves to `tickets/roadmap.md` and `notes.md` to `notes/notes.md`.

A ticket's artifacts stay inside its own folder (`tickets/0181-messages-wait/step-1/...`). Step paths and `runs.jsonl` therefore stay relative to the ticket folder, and `steps.py`, `run.sh`, and the verifiers, which take a task directory as an argument, do not change. The layout change is in the code that finds the task directory.

### What changes

| Component | Change |
| --- | --- |
| `tickets.py` | `ticket_root` default becomes `tickets`; reads `layout: flat` for old repos. Roadmap, router, `check`, `new`, `close`, `archive`, `number` use the resolved root. `check` fails on stray root content once `layout: topics` is set |
| `board.py`, `statusline.sh`, `traces/` | Resolve task dirs through `tickets.ticket_dir`, as `board.py` already does for `ticket_root` (T-0175). `traces/sources/tickets.py` already reads `ticket_root` |
| `fanout.py` | Does not support `ticket_root` yet (known limit, `.sdlc/notes.md`). It must resolve lane ticket roots through the same function. This is a prerequisite, not an option |
| Hooks | No hook names `.sdlc/` paths (checked: none under `hooks/`); no change |
| `onboard.py` | New repos get `layout: topics` and the folder entry files. Existing repos are untouched until they migrate |
| `check.py` | Guards that the entry files exist for each topic folder, and that docs name `tickets/` paths |
| Docs and skills | 38 files under `scripts/`, `hooks/`, `skills/`, and `agents/` mention `.sdlc`; the migration ticket updates the paths they print and the citing-file scan lists any that cite a moved folder |

### Compatibility with `ticket_root` today

`ticket_root: tickets` already exists and is opt-in (T-0175). The new default makes that setting implicit. A repo with the line keeps working, and a repo without it keeps the flat layout until it runs the migration, because changing a consumer's folders on upgrade is a breaking move.

### One-command migration

`tickets.py migrate-layout [--dry-run] [--rewrite-refs]`:

1. Refuses on a dirty tree or when ticket ids clash across worktrees.
2. Moves ticket folders into `tickets/`, task folders without a ticket into `work/`, and `notes.md` and `roadmap.md` to their folders.
3. Runs the existing citing-file scan (`close` and `archive` use it) for every moved folder and refuses naming each citing file, or rewrites the cites with `--rewrite-refs`.
4. Writes `layout: topics`, regenerates the router and roadmap, and runs `check`.
5. Is idempotent: a second run moves nothing.

`--dry-run` lists every move and every rewritten file and writes nothing.

## 4. Conductor batching and skipping (T-0192)

### Rule

Before any work, the conductor runs `steps.py lane` and follows it. After that, the conductor asks one question at every natural boundary: can this wait and be done once for a group? The rules below turn that question into checks.

### Batch

- **Plan reviews:** reviews required for several tickets in one fanout run are queued and run back to back on one model family. A later phase may let one reviewer run name several plans and return one verdict per plan; that changes the role contract, so it needs its own design and is not part of the first build.
- **Verification:** when several steps of one ticket are each at builder L1 to L3, are independent, and are all checkable on the final tree, one whole-ticket verifier replaces per-step verifiers. This is the branch verifier used for T-0175 to T-0184. Per-step verification stays for any step at L4 or L5, any merge step, and the `gates green` step.
- **Close-outs:** one `/open-questions` round per ticket set, not per ticket.

### Parallelize

Independent tickets run in `fanout` lanes when their declared file sets are disjoint and none is in another's `depends`. The planner lists the files it will change in a `Files:` line; `steps.py lane` and `fanout.py` check the overlap before launch. Shared generated files (roadmap, router, `check.py`, generated Codex agents) serialize by merge order. In this session the T-0175 merge into the T-0177 branch conflicted on duplicate planning files, and T-0185 had to wait for T-0184 to merge because both edit `check.py`; an overlap check would have made that ordering explicit.

### Skip, and record every skip

A role may be skipped only by an entry in the ticket's `skips.md` (one line: role, step, reason, who decided). `check` fails a closed ticket whose lane is `lean` or `fix` and that lacks the entry for any role the full chain would have run. `steps.py lane` writes the lane and reasons to the same file, so the choice is auditable.

### Never skipped

- The independent verifier on any step at builder L4 or L5, and on any merge step.
- The plan review that `steps.py review` requires (planner L3, steps at L4 or L5, a merge step, a replan).
- A focused live run for a role behavior change, and the checks in the root validation matrix.
- The filer when the builder or verifier reported follow-ups or warnings.
- The user's approval for any publish or external write, and any decision that is the user's to make.

These are the invariants in the repository and plugin `AGENTS.md`. Nothing in this design edits them.

## Build order

Each ticket is sized to plan at L2 where possible. L3 appears only where a ticket changes a contract other roles parse.

| Order | Ticket | Work | Plan level |
| --- | --- | --- | --- |
| A0 | new | `scripts/footprint.py`: files, bytes, and role runs per ticket, with a selftest. Gives every later target a measurement | L2 |
| A | T-0192 | `steps.py lane` and the conductor rule, `skips.md`, the `check` guard. Smallest, lands first | L2 |
| B | T-0189 | Lean lane text in chain and planner, coarse-step rule, the `steps.py lint` warning | L2 |
| C1 | T-0191 | Replan delta: `plan.md`, `plan-rev-<k>.md`, `split` applying revisions | L3 (parses plans) |
| C2 | T-0191 | Step handoffs by reference | L3 (changes `split`) |
| C3 | T-0191 | `## Carry forward` in scout, researcher, architect, archaeologist; reader rule in planner and builder | L2 |
| D0 | T-0190 | `fanout.py` honors `ticket_root` (prerequisite) | L2 |
| D1 | T-0190 | Layout resolver, `layout: topics`, `check`, `onboard.py` for new repos | L3 (touches `tickets.py` invariants) |
| D2 | T-0190 | `migrate-layout` with the citing-file scan | L3 |
| D3 | T-0190 | `board.py`, `statusline.sh`, `traces/`, docs and skills path updates | L2 |

Why this order: A and B change only decisions and guidance and pay back at once. C comes before D so migration moves the final file names once. D is last because it has the largest blast radius.

## Transition and migration

- Releases are additive. A and B ship as a patch; C ships behind a plan-format version line (`plan: 2`) that old plans lack, so `split` reads both. D ships `layout: flat` as the default for existing repos and `topics` for new ones, with `migrate-layout` and a documented upgrade note.
- A consumer on 0.20.x runs `tickets.py roadmap` once (as 0.20.2 required) and later `migrate-layout` when it chooses.
- A later minor release may flip the default for existing repos, after a `check` warning has run for one release.

## Risks

| Risk | Mitigation |
| --- | --- |
| Lean lane lets a risky change skip review | Lane is computed from facts, mandatory list matches `steps.py review`, skips need a record, negative controls prove refusal |
| Batched verification finds a failure late and the rebuild costs more | Batch only independent steps checkable on the final tree; keep per-step verification at L4/L5, merge, and gates |
| Replan deltas make a plan unreadable | `split` and a `plan.md --resolve` view print the merged plan; a delta that does not apply cleanly is refused |
| Migration breaks citations or ids | Reuses the existing citing-file scan, dry run first, idempotent, refuses on a dirty tree |
| `fanout.py` and `traces` miss the new layout | D0 and D3 are prerequisites with selftests on a topics-layout fixture |
| Contract text grows while the goal is to shrink it | Each ticket reports `footprint.py` before and after, and removes text as it adds |
| Codex parity | Lane and layout logic live in scripts both hosts run. Claude-only hooks are not part of this design, so no enforcement claim crosses hosts |

## Open questions

1. Lean thresholds: at most two steps and 12 criteria per step. Are these right for your repos?
2. Is whole-ticket batched verification acceptable at L3 builds, or only at L1 and L2?
3. `roadmap.md` and `notes.md` leave the `.sdlc/` root. Do other tools or docs in your repos read `.sdlc/roadmap.md` directly?
4. Migration: opt-in forever, or flip the default for existing repos after one release with a warning?
5. Who may record a skip: the conductor alone, or only after a user prompt for anything above size S?

## Validation plan

Every guard below has a positive case and a negative control.

| Behavior | Positive | Negative control |
| --- | --- | --- |
| `steps.py lane` | A size-S fixture gives `fix`, a two-step L2 plan gives `lean`, a planner L3 plan gives `full` | The same two-step plan with one step at L4 must give `full`, not `lean` |
| Skip record | A lean ticket with `skips.md` entries closes | A lean ticket missing an entry fails `check` |
| Lean verification independence | The lean verifier runs on a different family from the builder | A forced same-family run is refused by `run.sh` |
| Replan delta | A delta applies and `split` produces the merged plan | A delta naming a step that does not exist is refused |
| Step handoff by reference | The builder finds the anchored decision with only the step handoff and `plan.md` | A step handoff with a dangling anchor fails `steps.py lint` |
| Footprint targets | A fixture ticket on `full` and on `lean` shows the bytes and files reduction | A fixture that writes extra files fails the target check |
| `migrate-layout` | A fixture repo with cites migrates, `check` is clean, a second run is a no-op | A stray root folder fails `check`; a dirty tree is refused; an unrewritten cite is reported |
| Live runs | One lean ticket and one full ticket run end to end on Claude and Codex in a throwaway project, with the footprint recorded | A ticket that changes `steps.py` is routed to `full` by `lane` |

An independent verifier checks each build ticket, and the whole set gets a branch verifier before any release, as in 0.20.2.

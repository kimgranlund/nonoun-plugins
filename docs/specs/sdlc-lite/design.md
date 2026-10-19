# SDLC Lite design

Version 0.4, 2026-10-04. Proposal. Nothing here is built. Tickets T-0189, T-0190, T-0191, T-0192.

Superseded in part by 0.23.0 lean work records (T-0539 to T-0545): a ticket's committed record is its `handoff.md` (plus `skips.md` until a fanout close moves it), closed with a `## Outcome` that `tickets.py close` writes; role results, step folders, attempts and `runs.jsonl` live in the ignored records dir `.sdlc/runtime/tasks/<folder>/`; the filer runs only when asked (`/file`, `close --filer`). Statements below about where artifacts live and when the filer runs describe 0.22 and earlier.

v0.4 applies the second review's eleven findings. v0.3 recorded the user's decisions (see Resolved decisions) and applies the second independent review (`../validation/lean-sdlc-design-review-2.md`). v0.2 applied the first independent review (`../validation/lean-sdlc-design-review.md`, verdict not ready at v0.1): the plan record keeps the existing planner result names, batched verification needs a runner change first, the layout move is re-scoped around a path resolver, and the build order is re-cut so each file has one writer.

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

## Resolved decisions

Made by the user on 2026-10-04.

1. Batched verification waits for the runner change. `run.sh` and `codex_roles.resolve` are fixed so the verifier family rule fires for a verifier launched at the task directory, and `steps.py` learns the step state of a task-dir verifier result (rows V and S, added by the second review); after both, batching is allowed at any builder level (not pinned to verifier L3).
2. The lean lane always runs the filer. No new `close` gate.
3. `roadmap.md` and `notes.md` move out of the `.sdlc/` root into topic folders (`tickets/roadmap.md`, `notes/notes.md`), with a migration.

Defaults chosen by the author for the remaining questions, because the user asked for the safest option. Each is a default the user may change:

4. Lean thresholds: at most two steps and 12 criteria per step (the stricter end; raise only after `footprint.py` measures a fixture).
5. Migration: opt-in. Existing repos keep `layout: flat` and get a `check` warning that names `migrate-layout`; no release flips the default for them. New repos get `layout: topics`.
6. Skips: the conductor may record only a skip that `steps.py lane` permits for the current lane. Any other skip needs the user's approval through AskUserQuestion before it is recorded, at every size.

## Principles

1. Process follows risk. The full chain is for work whose failure is expensive or cross-cutting. Everything else takes a shorter lane, and the choice is made by a script, not by prose.
2. Write a fact once. A later role reads the earlier result and the files it cites. It does not re-derive them and it does not get a new copy of them.
3. The folder system explains itself (as T-0175 to T-0179 did). A role that opens any folder learns the rules from that folder's `AGENTS.md`.
4. Independent verification is not a cost to trim. Lean means fewer, larger units of verification, never unverified work.
5. Every skip is recorded and every guard can fail. A skipped role leaves a line a check can find, and each new guard ships with a negative control.

## 1. Lean chain (T-0189)

Today the lanes are `/fix` (ticket level L1, no planner) and `/chain` (everything else). A level L2 ticket pays for `/chain` in full. The change is a third lane between them and a planner rule that makes steps coarse.

### Lane selection

`steps.py lane <ticket dir>` (new) prints `solo`, `lean`, or `full` and the reasons, from facts the files already hold: ticket size (front matter has `size` and no owner or subsystem field, `tickets.py:185-190`), planner level, step levels, merge steps, and, after planning, the files in each step's scope allow-list (parsed with the forms `widen` already recognizes, `steps.py:1460-1485`). A.1 extracts a `review_required()` function from `review_action` (which inlines its reasons at `1230-1242`) and `lane` calls it; selftest `(r)` stays green. The conductor runs it and follows the first line, the way it follows `steps.py next`.

| Lane | Use when | Roles |
| --- | --- | --- |
| fix | ticket level L1, one file's behavior, no plan needed (unchanged) | builder L1 or L2, verifier L1 |
| lean | ticket level L1 or L2, every condition in the lean list below holds | planner L2, builder and verifier per coarse step, one close-out |
| full | any condition in the mandatory list below | the current chain, unchanged |

### Lean conditions (all must hold)

- Planner level L1 or L2 (never the cross-cutting L3 plan).
- At most two steps, and every step at builder L1 to L3.
- No merge step and no replan. A replan cannot be known at plan time, so `lane` is advisory and recomputed (see Decision points).
- The change stays within one nearest `AGENTS.md` owner, or one script and its tests, with no change to a contract that other roles parse (role output sections, `run.sh` tables, `steps.py`, `tickets.py` invariants, hooks).

### Full chain is mandatory when any holds

- Any step at builder L4 or L5, or an `unresolved:` assumption in the plan. Plan review is for L4 and L5 steps only (T-0294): planner L3, a merge step, a replan, and a `## Plan review` line no longer require it. These are the cases `steps.py review` requires a review or a stop for (`steps.py:103`, `1227-1242`). `lane` calls the same function `review` uses, so the two cannot disagree.
- The ticket changes role behavior, a runner invariant, a hook, or a check. A focused live run is still required (plugin guidance), and lean does not waive it.
- A step that touches shared generated state (roadmap, router, generated Codex agents) alongside other tickets in flight.

### Decision points

Before planning, size alone decides, with one limit: a ticket of level L1 or L2 with more than 20 checkbox criteria under `## Acceptance criteria` is `full`, with a reason that says to split it into tickets of at most 20 (T-0296). `lane` runs at three points and prints the same first-line contract each time: before planning (from ticket front matter only: size), after the planner result (adds step levels, merge steps, files), and after every append to `## Plan review` (a swap, a widen, a replan, or a review). A lean ticket that reaches a mandatory condition becomes `full` from that point; work already done stays valid and the conductor continues at the next required role. Each call appends its result to the ticket's `skips.md` header, so the lane history is auditable.

### Coarse steps

The planner rule changes from "one step per file or concern" to "one step per independently verifiable outcome". A step may hold up to a stated number of criteria (proposed 12) including its guards. Two steps with a sequential dependency, the same builder level, and no intermediate gate merge into one. The plan's `gates green` final step (planner rule 14) stays the place for whole-suite gates, so a lean ticket is one or two steps plus the gates inside the last one.

`steps.py lint` gains a warning, not a refusal, when a lean-eligible plan has more than two steps or a step with one criterion, so the planner sees the rule without a hard failure.

### Verification and review in the lean lane

- Plan review: not required, because a lean plan is a routine plan under the existing rule. The conductor may still request one.
- One verifier per step, which is already one per two steps at most. A verifier never runs on the builder's family (`run.sh` enforces it), so independence is unchanged.
- Close-out: `tickets.py close --reason` skips every filer gate (`tickets.py:83-85`) and reads no builder or verifier notes, so a rule "filer only when there are follow-ups" would be prose with no check. Decision for the user (open question 6): the lean lane always runs the filer (one Sonnet run, about 2 KB, keeps close's gates intact; recommended), or `close` gains a gate that reads the verifier result's follow-ups. `/fix` stays without a filer.

## 2. Single plan record (T-0191)

### Constraint

The pipeline fixes result names and reads them by name. `run.sh` writes every result as `<role>-<level>[-k].md` and requires `## Goal` in a planner result (`run.sh:17-21`, `186-191`). `order.py` ranks only files matching that pattern (`order.py:22`). `steps.py review` detects a replan as two or more `planner-*.md` files (`steps.py:1237`), `split` reads only the newest planner file, and the plan-reviewer reads the newest and reaches earlier ones only through `## Plan review` (`agents/plan-reviewer.md:10`). A file named `plan.md` is invisible to all of them, so this design keeps the existing names and changes what is written inside them.

### Changes

1. **Replan by delta, inside the existing names.** The first plan is `planner-L<n>.md`. A replan is the next planner result and carries a `revises: <planner file>` header and only the changed or added steps and the findings it addresses; unchanged steps are named by number. The replan is usually not a `-k` file: `run.sh` adds `-k` only when the same role and level reruns (`run.sh:187-192`), and `/chain` replans at planner L3 (`steps.py:1263`), so an L2 plan's first replan is `planner-L3.md`. `revises:` therefore names a file across levels, and the target "at most a quarter of the plan it revises" holds for an L3 delta. Delta handling keys on the presence of `revises:`; there is no plan-format version line.
   - **One merged view.** Every reader that takes a task directory picks the newest planner file alone today: `find_plan` (`steps.py:236-243`) feeds `cmd_lint` (`913-916`), and `review_action` reads `plan_facts(plans[-1])` (`1223-1226`). After a delta, `lint` would lint only the changed steps and `review` could not see a base `unresolved:` assumption or a base step at L4. So C1 makes `find_plan` return the merged plan for a directory target, and `split`, `lint`, `review`, `lane`, and `resolve` all use it. A delta that names a missing step is refused as a `plan defect:`.
   - **Replan split.** `steps.py split` without `--only` refuses when `step-1/` already holds results (`steps.py:863-889`), so the lean chain text says the replan split is `--only <changed steps>` after the supersede rename, as `/chain` 4.2 does today.
   - **Reviewer.** The plan-reviewer reads `steps.py resolve` output (the merged plan), so a chain of two deltas does not drop the base.
   - **Regression set.** The selftest `(r)` at `steps.py:2647` and the closed tickets with two planner files in `.sdlc/` guard the change to what `lint` and `review` see.
2. **Planner-written step blocks stop restating the plan.** `split` copies the goal and the planner's step block verbatim and adds no plan context (`steps.py:897`); in T-0181 step 1 the goal is 166 bytes and the planner-authored block is the other 12,900. So the fix is a planner rule and a lint, not a `split` change. The rule: a step block holds the criteria, scope, `### Read first`, and `### Do`, and cites a settled decision by anchor (`plan: <planner file>#<anchor>`) instead of restating it. `steps.py lint` resolves each anchor against the plan file named in the same step block (a step handoff carries no other plan reference) and refuses a dangling one.
3. **A `## Carry forward` section, written once.** The scout, researcher, archaeologist, and architect each end their result with a short `## Carry forward` section (at most 15 lines: facts and paths later roles must not re-derive). The planner cites the result path and does not copy it. Planner and builder contracts say to read `## Carry forward` before searching and to search only what it does not answer. This changes five role contracts and the generated Codex agents.
4. **What each role reads and writes.**

| Role | Reads | Writes |
| --- | --- | --- |
| scout, researcher, architect, archaeologist | ticket handoff | one result with `## Carry forward` |
| planner | ticket handoff, the `## Carry forward` sections | `planner-L<n>.md`, or a delta `planner-L<n>-<k>.md` |
| plan-reviewer | ticket handoff, newest planner file and the file it revises | one result |
| builder | its step handoff, the cited anchors in the plan, its `### Read first` files | one result, with files changed |
| verifier | its step handoff and the builder result | one result |
| filer | the ticket handoff, results by name | one record |

5. **Handoff files stay the roles' only brief.** Nothing here widens what a role may read beyond what it cites.

### Targets

For a two-step ticket on the lean lane: at most 14 files and 60 KB of `.md`, against T-0181's 51 files and 185 KB. Planner text at most 20 KB. These are proposals until `footprint.py` measures a fixture ticket on both lanes.

## 3. Topic sub-folders as the default layout (T-0190)

### Target layout

```
.sdlc/
  AGENTS.md            router (entry file, as today)
  CLAUDE.md            @AGENTS.md
  config               layout and ticket settings
  tickets/             NNNN-slug/ per ticket (handoff.md, skips.md); .NNNN-slug/ when closed
    AGENTS.md  CLAUDE.md  roadmap.md
  work/                <slug>/ for tasks with no ticket (release records, verification handoffs, dogfood runs)
    AGENTS.md  CLAUDE.md
  messages/            new/ read/ done/ (T-0177 to T-0179, unchanged)
  notes/               notes.md and its entry file
  evals/  proposals/  supervisor/    planned in T-0183 to T-0187 (still proposed); each gets its own entry file when built
  _templates/
  runtime/  dogfood/   git-ignored; runtime/tasks/<folder>/ holds each task's run records (0.23.0)
```

Root holds only the router, its import, `config`, `_templates/`, and the git-ignored `runtime/` and `dogfood/`. The target moves `roadmap.md` to `tickets/roadmap.md` and `notes.md` to `notes/notes.md`. That move is a user decision (open question 3): `tickets.py` hardcodes the root paths (`tickets.py:842, 851, 1231, 1308, 1547, 1595`), `ticket_dir` documents that they "stay at <root> either way" (`tickets.py:304`), the citing-file scan skips `<rel>/roadmap.md` by that path (`tickets.py:535`), `onboard.py:252` prints `.sdlc/roadmap.md` inside the managed `AGENTS.md` block (a template version bump for every consumer), `tickets.py roadmap` also regenerates `messages/AGENTS.md`, and ten files outside the plugin, including the repository root `AGENTS.md`, cite `.sdlc/roadmap.md`. The alternative leaves both files at the root and removes all of that, at the cost of the "root holds only entry files" rule.

A ticket's artifacts stay inside its own folder (`tickets/0181-messages-wait/step-1/...`); since 0.23.0 they stay in its records dir (`runtime/tasks/0181-messages-wait/step-1/...`), which `order.py records_dir` resolves from the task folder. Step paths and `runs.jsonl` therefore stay relative to the task, and `steps.py`, `run.sh`, and the verifiers, which take a task directory as an argument, do not change. The layout change is in one resolver (below) that returns the ticket directory, the roadmap path, and the notes path; every caller that today builds `root / 'roadmap.md'` goes through it.

### What changes

| Component | Change |
| --- | --- |
| `tickets.py` | A `layout: topics\|flat` config key beside `ticket_root`, and one function returning the ticket directory, roadmap path, and notes path. `ticket_root` stays explicit: other worktrees and external branches resolve a tree by its own `ticket_root` line (`tickets.py:375-420`), and `board.py:213`, `traces/ingest.py:68`, and `traces/sources/tickets.py:20` read it too, so a tree that wrote only `layout: topics` would look flat to every other tree. `migrate-layout` writes both lines; `layout` governs only roadmap, notes, `work/`, and strays Roadmap, router, `check`, `new`, `close`, `archive`, `number` use it. `check` fails on stray root content once `layout: topics` is set, and `check.py:330`, which pins the literal `.sdlc/<slug>/step-1/handoff.md` in the fix skill, takes the resolved form |
| `board.py`, `statusline.sh`, `traces/` | Resolve task dirs through `tickets.ticket_dir`, as `board.py` already does for `ticket_root` (T-0175). `traces/sources/tickets.py` already reads `ticket_root` |
| `fanout.py` | Does not support `ticket_root` yet (known limit, `docs/work/NOTES.md`). Lane ticket paths (`fanout.py:432, 508-510, 668, 678, 736, 746`) must go through `tickets.ticket_dir`. A prerequisite, not an option |
| Hooks | No hook names `.sdlc/` paths (checked: none under `hooks/`); no change |
| `onboard.py` | New repos get `layout: topics` and the folder entry files. `TEMPLATE_VERSION` (`onboard.py:219`) is part of the start marker, so a bump marks every existing block `stale` (`581-582`) and a rerun replaces it (`684`). To keep existing repos untouched, the managed block is rendered from the repo's resolved paths and a flat repo's text and version are unchanged; a topics repo renders the topics variant |
| Path residue | `traces/sources/tickets.py:28` hardcodes `root / 'notes.md'`; the router template names `roadmap.md` and `notes.md` at root (`tickets.py:894`); `write_roadmap` also regenerates `messages/AGENTS.md` (`tickets.py:842-846`), so D1 owns that text |
| Codex host skill | `skills/sdlc-lite/SKILL.md` has no `steps.py` mention today, so `steps.py lane` and `resolve` reach Codex only if that skill is changed. It is part of the lane ticket |
| `check.py` | Guards that the entry files exist for each topic folder, and that docs name `tickets/` paths |
| Docs and skills | 38 files under `scripts/`, `hooks/`, `skills/`, and `agents/` mention `.sdlc`; the migration ticket updates the paths they print and the citing-file scan lists any that cite a moved folder |

### Compatibility with `ticket_root` today

`ticket_root: tickets` already exists and is opt-in (T-0175). The new default makes that setting implicit. A repo with the line keeps working, and a repo without it keeps the flat layout until it runs the migration, because changing a consumer's folders on upgrade is a breaking move.

### One-command migration

`tickets.py migrate-layout [--dry-run] [--rewrite-refs]`:

1. Refuses on a dirty tree. Id uniqueness is not a precondition: each worktree resolves its own ticket root from its own config (`tickets.py:122-129`), so a migrated tree beside a flat one keeps ids unique, and `check` reports a clash after merge.
2. Moves ticket folders into `tickets/`, task folders without a ticket into `work/`, and `notes.md` and `roadmap.md` to their folders.
3. Runs the existing citing-file scan (`close` and `archive` use it, `outside_refs` at `tickets.py:510-535`) for every moved ticket folder. That scan looks for folder literals `<rel>/<slug>`, so the two file moves (`roadmap.md`, `notes.md`) need their own cite scan. It refuses naming each citing file, or rewrites the cites with `--rewrite-refs`. Dated records under `docs/reports/` are never rewritten (repository `AGENTS.md`); five of the ten outside citers are such records, and the others (the root `AGENTS.md`, plugin guidance, docs) are listed in the dry run.
4. Writes `layout: topics`, regenerates the router and roadmap, and runs `check`.
5. Is idempotent: a second run moves nothing.

`--dry-run` lists every move and every rewritten file and writes nothing.

## 4. Conductor batching and skipping (T-0192)

### Rule

Before any work, the conductor runs `steps.py lane` and follows it. After that, the conductor asks one question at every natural boundary: can this wait and be done once for a group? The rules below turn that question into checks.

### Batch

- **Plan reviews:** reviews required for several tickets in one fanout run are queued and run back to back on one model family. A later phase may let one reviewer run name several plans and return one verdict per plan; that changes the role contract, so it needs its own design and is not part of the first build.
- **Verification:** when several steps of one ticket are each at any builder level except where per-step verification stays mandatory, are independent, and are all checkable on the final tree, one whole-ticket verifier replaces per-step verifiers. Per-step verification stays for any step at L4 or L5, any merge step, and the `gates green` step. Two runner pieces come first:
  - **Family rule (row V).** The family rule reads the newest builder in the verifier's own handoff dir (`run.sh:198-207`; `codex_roles.resolve` has the same shape, `codex_roles.py:100-120`). A verifier launched at the task dir finds no builder there, so the rule never fires. The branch verifier this design cites as its model ran in `.sdlc/verify-ticket-stages/step-1/` with no builder result, so its family was not enforced. Verifier L1 and L2 are Sonnet and builder L1 is Sonnet (`run.sh:102, 111-112`). The fix makes the rule read any step's newest builder (superseded step directories excluded) when the handoff dir holds none.
  - **Step state (row S).** `steps.py next` and `resume` read `step-<n>/` only (`steps.py:1016-1053, 1123-1145`), `board.py` renders per step (`board.py:104-137`), and `order.py` compares line ranks inside one `runs.jsonl` (`order.py:103-110`) while `run.sh` writes `runs.jsonl` per handoff dir (`run.sh:470`). A task-dir verifier is invisible to all of them: `resume` would print `verify` for every step and a rebuild after the batch would go undetected. The rule: a task-dir verifier result lists the builder result files it verified, and `next` and `resume` treat a listed, unchanged step as verified; `board.py` renders it. A step whose builder result is newer than the listing is not verified.
  Resolved decision 1 reads "after rows V and S". Until both ship, batched verification is not used; once they ship it is allowed at any builder level. If row S grows into a larger `steps.py` change than expected, batching is deferred to a later release rather than shipped as half a rule.
- **Close-outs:** one `/open-questions` round per ticket set, not per ticket.

### Parallelize

Independent tickets run in `fanout` lanes when their file sets are disjoint and none is in another's `depends`. Lanes plan inside the lane (`fanout.py:432`), so no plan exists at launch and a separate `Files:` line would be a second copy of a fact the plan already holds (planner rules 6 and 35 put each step's files in its scope criterion, so a `Files:` line would also break principle 2). The overlap check therefore has two points: for tickets already planned, from their scope criteria; and at merge time, from `git diff --name-only` of each lane against the integration branch, which fanout's locked merge already serializes. Shared generated files (roadmap, router, `check.py`, generated Codex agents) serialize by merge order. In this session the T-0175 merge into the T-0177 branch conflicted on duplicate planning files, and T-0185 had to wait for T-0184 to merge because both edit `check.py`; an overlap check would have made that ordering explicit.

### Skip, and record every skip

A role may be skipped only by an entry in the ticket's `skips.md` (one line: role, step, reason, who decided). The guard lives in `tickets.py check` and `close` (`tickets.py:1508-1514, 1300`), not in `check.py`, which checks plugin contracts and never runs in a consumer repo (`check.py:1-40`). It fails a closed ticket whose lane is `lean` or `fix` and that lacks the entry for any role the full chain would have run, and it exempts tickets closed before the feature (every existing `/fix` ticket has no `skips.md`), so `check` does not go red on upgrade. `steps.py lane` writes the lane and reasons to the same file, so the choice is auditable.

### Never skipped

- The independent verifier on any step at builder L4 or L5, and on any merge step.
- The plan review that `steps.py review` requires (steps at L4 or L5 only).
- A focused live run for a role behavior change, and the checks in the root validation matrix.
- The filer when the builder or verifier reported follow-ups or warnings (0.22; since 0.23.0 `tickets.py close` takes follow-ups from the verifier's `## Notes` and the filer runs only when asked).
- The user's approval for any publish or external write, and any decision that is the user's to make.

These are the invariants in the repository and plugin `AGENTS.md`. Nothing in this design edits them.

## Build order

Each ticket is sized to plan at L2 where possible. L3 appears only where a ticket changes a contract other roles parse.

| Order | Ticket | Work (one owning file group per row) | Plan level | Depends |
| --- | --- | --- | --- | --- |
| L1 | T-0189 | `footprint` (A0): `scripts/footprint.py`, a selftest, and `footprint.py check --max-files --max-bytes` so a target is a gate. Measurement and its target check | L2 | none |
| L2 | T-0189 | `lean-lane-text` (B): `skills/chain`, `agents/planner.md` coarse-step rule, `steps.py lint` warning. Lands before `lane` so `lane` never prints `lean` without a lean lane | L2 | none |
| L3 | T-0192 | `runner-family-task-dir` (V): `run.sh:198-207` and `codex_roles.resolve`: the family rule reads any step's newest builder (superseded dirs excluded) when the handoff dir has none; `run-selftest.sh` task-dir fixture (prints `--model sonnet` before, `--model opus` after) and a `codex-selftest.py` case (`resolve` returns `shared` false with no builder today). Negative control is the pre-fix output | L3 | none |
| L4 | T-0192 | `batch-state` (S): `steps.py next` and `resume` treat a builder result listed by a task-dir verifier result as verified when unchanged; `board.py` renders it | L3 | L3 |
| L5 | T-0192 | `lane` (A1a): `steps.py lane`, `review_required()` extracted from `review_action`, `skips.md` writer, Codex host skill mention | L3 | L2 |
| L6 | T-0192 | `skips-guard` (A1b): `tickets.py check` and `close` guard with the pre-feature exemption | L2 | L5 |
| L7 | T-0192 | `conductor-rules` (A1c): `agents/conductor.md`, chain batching and skip text, filer-always on lean, AskUserQuestion for non-permitted skips, `codex_roles.py generate` | L2 | L4, L6 |
| L8 | T-0191 | `plan-merge` (C1): merged view for `find_plan` dir targets, `resolve`, cross-level `revises:`, missing-step refusal, replan `--only` text, `plan-reviewer.md` read rule | L3 | L5 |
| L9 | T-0191 | `anchor` (C2): planner anchor rule and `steps.py lint` anchor check | L2 | L8 |
| L10 | T-0191 | `carry-forward` (C3): `## Carry forward` in four producing contracts, planner and builder reader rule, regenerate, focused live run | L3 | none |
| L11 | T-0192 | `fanout-overlap`: merge-time `git diff --name-only` overlap check in `fanout.py` (section 4 Parallelize) | L2 | none |
| L12 | T-0190 | `fanout-resolver` (D0): fanout lane paths through `tickets.ticket_dir` | L2 | L11 |
| L13 | T-0190 | `layout-resolver` (D1): `tickets.py` `layout` key and the resolver (ticket dir, roadmap, notes), strays, router text, `messages/AGENTS.md` text, `onboard.py` variants without a bump for flat repos | L3 | L12 |
| L14 | T-0190 | `migrate-layout` (D2): both config lines written, file-cite scan for `roadmap.md` and `notes.md`, the listed citers | L3 | L13 |
| L15 | T-0190 | `layout-readers-docs` (D3): `board.py`, `statusline.sh`, `traces/sources/tickets.py:28`, docs and skills path updates | L2 | L14 |
| L16 | T-0189 | `live-evidence`: one lean and one full ticket on Claude and Codex with footprint recorded | L2 | L7, L9, L15 |

Filed 2026-10-04 as proposed tickets: L1 T-0193, L2 T-0194, L3 T-0195, L4 T-0196, L5 T-0197, L6 T-0198, L7 T-0199, L8 T-0200, L9 T-0201, L10 T-0202, L11 T-0203, L12 T-0204, L13 T-0205, L14 T-0206, L15 T-0207, L16 T-0208, each with its `depends` set from the Depends column. T-0189 to T-0192 are closed as superseded.

Rows that share a file run in sequence, never in parallel lanes.

Why this order: L1, L2, L3, L10, and L11 have no dependencies and can be filed and planned at once (rows that share a file still run in sequence). The runner and step-state pieces (L3, L4) come before the conductor rules that use them. Plan work (L8, L9) comes before layout so migration moves final file names once. Layout is last because it has the largest blast radius. T-0189 to T-0192 are the original four tickets; the sixteen rows supersede them.

## Transition and migration

- Releases are additive. Lane, skips, and batching ship as a patch; deltas ship keyed on the presence of `revises:`, so `split` reads old plans unchanged (no version line). Layout ships `layout: flat` as the default for existing repos and `topics` for new ones, with `migrate-layout` and a documented upgrade note. Existing repos see a `check` warning that names `migrate-layout` and nothing else changes.
- A consumer on 0.20.x runs `tickets.py roadmap` once (as 0.20.2 required) and later `migrate-layout` when it chooses.
- A later minor release may flip the default for existing repos, after a `check` warning has run for one release.

## Risks

| Risk | Mitigation |
| --- | --- |
| Lean lane lets a risky change skip review | Lane is computed from facts by the same function `review` uses, recomputed at each decision point, skips need a record, negative controls prove refusal |
| Batched verification finds a failure late and the rebuild costs more | Batch only independent steps checkable on the final tree; keep per-step verification at L4/L5, merge, and gates |
| Replan deltas make a plan unreadable | `steps.py resolve` prints the merged plan; a delta that does not apply cleanly is refused |
| Migration breaks citations or ids | Reuses the existing citing-file scan, dry run first, idempotent, refuses on a dirty tree |
| `fanout.py` and `traces` miss the new layout | D0 and D3 are prerequisites with selftests on a topics-layout fixture |
| Contract text grows while the goal is to shrink it | Each ticket reports `footprint.py` before and after, and removes text as it adds |
| `steps.py` merged view changes what `lint` and `review` see for every task with two planner files | Selftest `(r)` (`steps.py:2647`) and the closed tickets with two planner files are the regression set |
| Row S grows beyond a small rule | Defer batching to a later release rather than ship half a rule |
| Codex parity | Lane and layout logic live in scripts both hosts run. Claude-only hooks are not part of this design, so no enforcement claim crosses hosts |

## Open questions

None blocking (second review: no new user decision). Questions 1, 4, and 5 of v0.2 are settled by the defaults under Resolved decisions, which the user may change. Questions 2, 3, and 6 are resolved decisions.

## Validation plan

Every guard below has a positive case and a negative control.

| Behavior | Positive | Negative control |
| --- | --- | --- |
| `steps.py lane` | A level L1 fixture gives `solo`, a two-step L2 plan gives `lean`, a planner L3 plan gives `full` | The same two-step plan with one step at L4 must give `full`; a lean ticket whose handoff gains a `## Plan review` line flips to `full` on the next call |
| Skip record | A lean ticket with `skips.md` entries closes | A lean ticket missing an entry fails `check` |
| Batched verification independence | A task-dir verifier of Sonnet builds runs on a non-Sonnet family and the run record names it (after row V) | The pre-fix run: `run-selftest.sh` dry-runs the family rule on a task-dir fixture (cf. `run-selftest.sh:132-147`) and prints `--model sonnet` before the fix; `codex-selftest.py` resolve cases (cf. `256-262`) show `shared` false with no builder. `run.sh` remaps silently and has no refusal path, so the control asserts the remap |
| Batched step state | A task-dir verifier result listing the builder results makes `next` and `resume` treat those steps as verified, and `board.py` renders it | A step whose builder result is newer than the listing, or one not listed, still resumes at `verify` |
| Replan delta | A delta in `planner-L3-2.md` with `revises:` applies and `split` produces the merged plan; the plan-reviewer reads both | A delta naming a missing step is refused with a `plan defect:` last line |
| Step block by reference | The builder finds the anchored decision with only the step handoff and the planner file | A step block with a dangling anchor fails `steps.py lint` |
| Footprint targets | A fixture ticket on `full` and on `lean` (with one swap, since a swap appends `## Plan review` and flips lane) shows the bytes and files reduction | `footprint.py check --max-files` fails a fixture that writes extra files (L1 builds this check) |
| `migrate-layout` | A fixture repo with cites migrates, `check` is clean, a second run is a no-op | A stray root folder fails `check`; a dirty tree is refused; an unrewritten cite is reported |
| Live runs | One lean ticket and one full ticket run end to end on Claude and Codex in a throwaway project, with the footprint recorded | After planning, a ticket whose scope allow-list names `steps.py` is routed to `full` by `lane` (decision point 2; before planning, size alone decides) |

An independent verifier checks each build ticket, and the whole set gets a branch verifier before any release, as in 0.20.2.

# Plan doc format

One Markdown file, normally `.sdlc/<plan-slug>/plan-doc.md`, beside the run records it causes (attempt files, `plan-state.json`). Goals and KPIs stay in `docs/goals/` and `docs/kpi/` and are cited by id; the plan doc holds only execution. `plan_check.py plan` lints it and `plan_done.py` reads it through the same parser (`plan_doc.py`), so the two cannot disagree on what a step is.

## Front matter

```
---
id: PD-<slug>
title: <one line>
status: draft | approved | running | done | stopped
goal: G-002                    # a goals/ id, or `none: <reason>`
driver: sonnet-high            # the session that runs run-plan; recorded, not enforced
approved_by: maintainer
approved_on: 2026-10-09        # required once status is approved or later
reviewed: <plan-reviewer result path>   # required when any step is size L4 or L5
---
```

## Sections, in order

| Section | Holds |
|---|---|
| `## Goal` | One paragraph: what the steps build |
| `## Outcome` | The lines of the plan-verification outcome block: `Outcome:` with `Why:`, `Measured by:`, `Rubric:`, `Negative control:` |
| `## Measures` | Table `id, command, read, target, direction, before, when`. The command is backticked and read-only: no `rm`, no push or publish command, no `gh `, no `curl -X`, no `>` redirect. `read` is never empty: a dotted path into the JSON the command prints, or any label (`value`) when it prints one bare number (a command that prints `path:count`, as `git grep -c` does, is `unreadable`: reduce it to one number, for example `git grep -l X | wc -l`). A measure id is a letter, a dash and digits (`K-002`, `M-001`); `Done when` names it. `when` is `now` or `later: <owner>, <date or event>` |
| `## Authorization` | `The run MUST NOT ...` lines, then `Authorized:` and what the run may do beyond editing the repository and running checks, each with its condition |
| `## Budget and stop rules` | Total dollar cap, per-step caps, three 529s in a row, a rate or weekly limit, `replan cap: 1, then stop`, and the notes path (`.sdlc/notes.md`, or `.sdlc/notes/notes.md`) |
| `## Step <n>: <title>` | One block per ticket (below) |
| `## Upserts` | Table `path, mode, step`: every corpus record the run creates, edits or retires; mode is `create`, `edit` or `retire`; one step owns each path |
| `## Later measures` | Optional table `id, read, owner, date` for a KPI that moves only with elapsed time; it never gates `plan_done.py` |
| `## Done when` | The `plan_done.py` exit rule and the fenced `Goal line:` |

## Step block

```
## Step 3: <title>
level: L2                       # the ticket size, L1 to L5
ticket: T-0413                  # an existing id, or `new feature <slug>`
depends: [2]                    # earlier step numbers only
executor: auto                  # auto, or a levels.json row such as solo-L2 or builder-L3
verify: auto                    # auto (size L2 and above), or required
cap: $12                        # dollar ceiling; becomes the ticket's budget_usd
upserts: [docs/references/x.md]
### Read first
### Do
### Acceptance criteria
- (red) `...`
- (guard) `...`
```

For `ticket: new`, run-plan creates the ticket with `tickets.py new` and copies Do and Acceptance criteria into its handoff once; after a role has read that handoff it is frozen and a change is a replan. For an existing ticket the step's criteria read `see ticket` or equal its Done when.

## Lint rules (`plan_check.py plan`)

A FAIL is one rule id: `plan-front`, `no-approval` (with `--run`: status must be approved or running, with `approved_by` and `approved_on`), `outcome-block`, `done-measured`, `measure-row`, `measure-safe`, `later-named`, `step-shape`, `depends-order`, `cap-sum`, `executor-unknown`, `verifier-seat`, `review-missing`, `upsert-shape`, `upsert-sweep`, `authorization`, `stop-rules`, `goal-line`, `done-plan-done`. Warnings: `l1-unverified`, `kpi-drift`, `kpi-unresolved`, and the controlled-language `hedge`, `verb` and `rfc2119` (the plan rules). Run `plan_check.py plan --file <plan-doc.md> --run` before a run starts; it must exit 0.

## Goal line

The last fenced block of Done when, one line. It must name this file's own path and the `plan_done.py` command (write the resolved plugin path, since the stop hook cannot expand a variable):

```
/goal complete build and verify <plan-doc.md> by the run-plan skill: done when `python3 <plugin-root>/scripts/plan_done.py <plan-doc.md>` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote the state. Do not end the turn while it exits 1 and an item is open that you can work on.
```

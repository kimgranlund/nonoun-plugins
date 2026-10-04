# Lean SDLC cost control

Version 0.1, 2026-10-04. Proposal addendum to [the lean design](design.md). Nothing here is built. It adds four items the lean tickets T-0193 to T-0208 do not cover. It changes no model or effort default.

## Problem

Role runs on 2026-10-04 cost about $190 over 75 runs (recounted from every `runs.jsonl` in the repository and its worktrees, deduplicated by `attempt_id`). The cost is concentrated where plans are written and checked, not where code is written.

| Role | Runs | Cost | Share |
| --- | --- | --- | --- |
| planner L3 | 9 | $51 | 27% |
| verifier L3 (branch and release) | 8 | $43 | 22% |
| plan-reviewer | 10 | $41 | 21% |
| builders | 24 | $35 | 18% |
| architect | 2 | $12 | 6% |
| everything else (verifier L1 and L2, planner L1 and L2, filer) | 22 | $7 | 4% |

Counted 2026-10-04 00:00 to 17:32 UTC. Per ticket (build tickets only): T-0203 $14.5, T-0185 $16.7, T-0202 $21.2, T-0197 $23.1, T-0195 $27.6, T-0183 $36.4 (still open). Median about $22.

The runs record only `run.sh` roles. The conductor and background agent sessions are not in `runs.jsonl`, so the true spend is higher.

Why it is high, from this week's evidence:

- Four of seven plans (T-0183, T-0184, T-0195, T-0197) came back from plan review with verdict `replan`, and T-0202 was replanned at step 2 after a build-time defect. T-0195 was reviewed three times. Each replan is another planner L3 run and another plan-review run, about $10 together (planner L3 averages $5.70, a plan review $4.10).
- The reviewer findings in those four replans (10 in total) split into two kinds. Three are mechanical: two criteria already green when their step starts, so they cannot go red for the step's behavior (T-0183 step 3), and a `(guard)` criterion running `check.sh` under a 300-second guard timeout when the command takes about 255 seconds or more on this host, so `steps.py split --only` refuses (T-0183 step 7, T-0195 step 4). Seven are judgment: criteria that omit design rows, an unnamed contract dependent, a call that raises on a handoff with no front matter, a layout record not updated, an impossible order criterion, a control body that does not match the wake.
- A handoff edited while a planner read it wasted whole runs. Six scope additions to T-0176 invalidated running planners; the first T-0175 planner hit its 30-minute limit with no plan.

So a mechanical gate removes about a quarter of replans and 30 percent of findings. It is worth building because it costs nothing per run, but it is not the main lever. The judgment findings need a better-informed planner and a cheaper way to re-review, which is items C and D.

## Conductor text is T-0199's

T-0199 (`.sdlc/0199-conductor-rules`, commit 36875d4 on main) owns `agents/conductor.md` and the conductor's objective, lane-first routing, the `Lane: <lane> because <reason>` line, and the stop rules, including that a second replan verdict, or a ticket past its budget once the budget ticket lands, is a hard stop that comes to the user. Nothing below restates that text. Each item names only the machinery T-0199's text calls (a script, an exit code, a file), and where an item needs one more conductor sentence, it lands as a change to T-0199's text after T-0199 merges, never as a parallel edit. T-0209 (maintainer lean default, filed on main) is the maintainer-side line and is also not repeated here.

## What already exists

Do not rebuild these. The addendum extends them.

- `steps.py lint` checks that criteria parse, hold no `||` fallback, pin no sha, compare no changing count, and require no clean porcelain status. It prints coarse-step warnings. It never executes a span.
- `steps.py split --only N` runs a step's `(guard)` criteria against the current tree under `--guard-timeout` (default 300), refuses a red guard, a timeout, or a tree change.
- `steps.py review` already stops after two `replan` verdicts in a task dir. The cap exists. What is missing is a measure of it and a cheaper path before it triggers.
- `board.py` already sums `cost_usd` across `step-*` dirs (superseded dirs count).
- `run.sh` writes `<role>-<level>.attempt.json` and one `runs.jsonl` line per run; `run_lifecycle.py` owns the attempt record.

## A. Spec gate

A deterministic check that catches the mechanical plan defects before any plan-reviewer runs.

### Gap

`lint` is static and never runs anything. Two classes escape it: a negative control that is already green on the base (so it cannot detect the change), and a guard that cannot finish inside its timeout.

### Design

New script `scripts/specgate.py`, with a data file `scripts/slow-commands.json` (command pattern to measured seconds, seeded with `check.sh`). Subcommands:

- `specgate.py check <plan | task dir>`: static, read-only, exit 0 or 1. Findings: a `(guard)` span matching a `slow-commands.json` pattern whose seconds exceed the plan's guard timeout, printing the `--guard-timeout` the split needs; a criterion whose text names a negative control but carries no `(red)` tag (warning).
- `specgate.py red <plan | task dir> [--step N] [--timeout S]`: for each criterion tagged `(red)`, create a detached worktree at `$SDLC_BASE_SHA` (or `HEAD`) under `SDLC_TMP_WORKTREES`, run the criterion's command spans there, and require a nonzero exit. A zero exit refuses with `red-first: step <n>: <span> is green on the base; it cannot detect the change`. A timeout refuses. The worktree is removed on every path.
- `specgate.py measure <command>`: runs the command once, records its seconds in `slow-commands.json`.
- `specgate.py selftest`.

`(red)` is a new criterion tag next to `(guard)`. A `(guard)` is a precondition that must be green now; a `(red)` is a control that must be red now and green after the step. A step tagged both on the same span is a lint finding.

Wiring, in two rows owned in order:

1. `run.sh` refuses to launch the `plan-reviewer` role while `specgate.py check` on the plan has findings, printing them, so the conductor sends the plan back to the planner at no review cost. `SDLC_SPECGATE=off` skips it and the run record notes `specgate: off`.
2. `steps.py split` and `steps.py review` run `specgate.py check`, and `split --only N` also runs `specgate.py red` for that step beside its guards.

### Files

New: `scripts/specgate.py`, `scripts/slow-commands.json`. Edited: `scripts/run.sh` (row 1), `scripts/steps.py` (row 2), `skills/handoff-format/SKILL.md` (the `(red)` tag), `agents/planner.md` (use `(red)` for controls), `scripts/check.sh` and `scripts/check.py` (selftest wiring and a tag-consistency guard), `docs/maintenance/sdlc-internals.md`.

### Ordering

`run.sh` is edited by T-0195 and by item B and D below. `steps.py` is edited by T-0196, T-0197, T-0200 and T-0201. Item A waits for T-0195 and T-0201, then owns `run.sh` and the `steps.py` split and review paths until it merges. Plan level L3 (it changes a contract the planner and reviewer parse).

### Risks

- A `(red)` command with side effects. It runs in a throwaway worktree with no network flag; the base worktree is never the project tree.
- Cost of running `red` at split time. It runs once per step and the 300-second timeout bounds it.
- `slow-commands.json` goes stale. `measure` is cheap, and a finding names the stale entry.

### Validation

- Positive: a plan with a slow guard and a `(red)` control that is red on the base passes.
- Negative controls: a guard of `check.sh` under the default timeout is refused with the needed timeout; a `(red)` criterion that is already green on the base is refused; `run.sh plan-reviewer` on a failing plan exits before any model call (no `runs.jsonl` line, no `.running`). Each is shown to fail first by running the pre-change code or by a patched copy.
- Re-measure: replay the four 2026-10 replan findings. The gate must flag the three mechanical ones and none of the seven judgment ones.

## B. Handoff freeze

### Gap

Nothing detects that a handoff changed while a role read it. The role finishes, the result is recorded, and it answers an input that no longer exists.

### Design

- `run_lifecycle.py` records `handoff_sha256` (the file's sha256 at launch) in `<role>-<level>.attempt.json` and in the `runs.jsonl` line, next to `attempt_id`.
- At completion it hashes the handoff again. A difference sets `stale_input: true` on the run line and prints `run.sh: stale input: <handoff> changed while <role> ran` on stderr. The exit code stays as the role produced it so existing callers are unchanged.
- `steps.py next`, `resume` and `review` treat a result whose run line has `stale_input: true` like an invalid result: the action is `rerun`, with the reason `stale input`. A rerun that sees no change clears itself because the new run line is newer.
- Claude only: a PreToolUse hook `block-handoff-edit.sh` denies Edit, Write and MultiEdit on a path named `handoff.md` when a `*.running` file sits beside it, with a message saying to wait or to send one batched change request. The hook is an addition, not the only control: the stale-input flag works on both hosts and in a session with no hooks.
- A change request is a single `change.md` appended in the task dir by the conductor between runs; the next planner or builder handoff cites it. The conductor rule (T-0199 text) says to batch edits into one change request and launch after it.

### Files

Edited: `scripts/run_lifecycle.py`, `scripts/run.sh` (stderr line only if the lifecycle script does not print it), `scripts/steps.py` (next, resume, review treat stale input), `hooks/hooks.json`, new `hooks/block-handoff-edit.sh`, `scripts/hook-selftest.sh`, `docs/maintenance/claude-hooks.md`, `skills/chain/SKILL.md` (the change request rule, one sentence referencing T-0199's batching text), `scripts/check.py`. `agents/conductor.md` is T-0199's file: B adds no conductor text beyond a pointer line, and only after T-0199 merges.

### Ordering

After T-0195 (`run.sh`, merged), T-0196 (`steps.py next` and `resume`), T-0199 (`conductor.md`) and item A (`run.sh`, `steps.py`), because it edits the same functions and files. Plan level L3.

### Risks

- A legitimate edit during a run. The hook message names the escape: stop the run, or write `change.md`. The planner and filer never edit their own handoff.
- A hash taken of a path the runner rewrites. The handoff dir excludes the runner's own files, and the hash covers only `handoff.md`.
- Hook gaps on Codex. The flag still works; only the pre-edit denial is Claude-only. State this in the docs.

### Validation

- A selftest that edits `handoff.md` between launch and completion, with a stub role, sets `stale_input: true`, and `steps.py next` returns `rerun`.
- Negative controls: the same run with no edit is not flagged; a role that never reads the handoff but whose handoff changed is still flagged (the hash, not the role, decides); an edit to a sibling file is not flagged.
- Hook: a deny case with a `.running` file beside the handoff, an allow case without it, and an allow case for another file name.
- Live: one real planner run on Claude and one on Codex, with an edit made mid-run, ends in `rerun`.

## C. Replan as a delta, and a planner checklist

### Gap

A replan today is a new planning run that rereads the repository. The seven judgment findings above are code-reading defects the first plan missed. Cheaper re-review and a planner that avoids the known classes both reduce the loop.

### Design

1. Replan input. `steps.py replan-handoff <task dir>` writes a handoff for the replan that names the previous plan, the reviewer's findings by step, and the instruction to change only the affected steps and return a delta file with `revises:` (the format owned by T-0200). The planner then reads one plan and one findings list instead of rescouting. T-0202 carry-forward sections supply the research so it is not repeated.
2. Planner checklist, derived from the findings corpus. `agents/planner.md` gains a short pre-submission list built from the finding classes in the problem section: every design row or goal clause has a criterion; every untagged criterion fails at the start of its step; every function the step calls is named with its failure input (no front matter, empty file); every new file is listed in the layout record that enumerates files; guard commands fit the timeout. One line each, no prose.
3. Scoped review. `agents/plan-reviewer.md` gains a rule: after `specgate.py check` passes, review only the judgment items (goal coverage, interfaces, hidden dependents) and do not re-verify what the gate checked. A re-review after a delta reads the delta and the findings it answers, not the whole plan.
4. Cap and measure. The existing stop after two `replan` verdicts stays, and the conductor's hard stop on a second replan is T-0199 text (d); this item adds no conductor wording. `footprint.py` gains `replans` (the count of planner results beyond the first, and plan-reviewer `replan` verdicts), so the target below is a gate and not a story.

The option to run delta re-reviews at a lower effort is a model and effort decision and is left to the user (open question 1). Nothing here changes `run.sh` models or `models.json`.

### Files

New: `steps.py replan-handoff`. Edited: `scripts/steps.py`, `agents/planner.md`, `agents/plan-reviewer.md`, `scripts/footprint.py`, `scripts/codex_roles.py generate` output (agent bodies), `skills/chain/SKILL.md`, `scripts/check.py`.

### Ordering

After T-0200 (delta format), T-0201 (anchor rule edits `planner.md` and lint), T-0202 (planner reader rule) and item A (reviewer reads the gate). `steps.py` and `planner.md` have one writer at a time. Plan level L3.

### Risks

- A checklist that grows. Each line must cite a finding in a dated record; a line with no citation after two releases is removed.
- A delta that hides a cross-step effect. `steps.py resolve` (T-0200) merges the view and lint runs on the merged plan.

### Validation

- A selftest for `replan-handoff` output on a seeded task dir with a `replan` verdict.
- Negative control: a replan handoff for a task dir with no `replan` verdict is refused.
- Replay: feed the four 2026-10 replan findings through the checklist as a rubric on the original plans and count how many it names before review; record the count and the misses in the validation doc.
- `footprint.py` selftest for the `replans` field, with a seeded multi-planner task dir.

## D. Per-ticket cost budget

### Gap

Nothing meters spend. `board.py` sums cost per task for display, but no limit exists and the conductor never sees a number to react to.

### Design

- Front matter `budget_usd: <number>` on a ticket, optional, set at filing. Tier defaults from this week's medians: size S $5, M $30, L $60, XL none (ask). These are defaults the user may change (open question 2).
- New `scripts/budget.py`: `budget.py status <ticket dir>` prints `spend`, `budget`, `percent`, and `state` (`ok`, `warn` at 80 percent, `over` at 100); exit 0 ok, 3 warn or over, 2 no budget set. Spend is `cost_usd` summed from every `runs.jsonl` under the ticket folder and its step and superseded dirs, deduplicated by `attempt_id`. `budget.py set <ticket> --tier S|M|L` writes the field. `budget.py ack <ticket dir> --usd N --reason TEXT` writes `budget-ack.md` raising the ceiling once.
- `run.sh` pre-launch (after item B's edits): when the handoff dir's ticket has a budget and `budget.py status` is `warn` or `over` with no later `budget-ack.md`, exit 3 with `run.sh: budget <pct>%: ask the user; budget.py ack`. T-0199's stop rule (d) turns this into one question to the user. A ticket with no budget is unmetered, so existing repos see no change.
- `board.py` shows `$spend/$budget` per ticket and marks 🟡 at 80 percent and 🔴 over.

Limit: spend covers `run.sh` roles only. Conductor and background agent sessions are not in `runs.jsonl`, so the budget bounds the pipeline, not the session. State this in the entry file.

### Files

New: `scripts/budget.py`. Edited: `scripts/run.sh` (gate), `scripts/board.py` (column), `skills/ticket/SKILL.md` (set at filing). The conductor's stop on a ticket past its budget is T-0199 text (d); `run.sh` exit 3 is the machinery it calls, so `agents/conductor.md` is not edited here, `scripts/check.sh`, `scripts/check.py`, `docs/maintenance/sdlc-internals.md`. `tickets.py` is not edited: it does not validate `budget_usd`, like `claimed_by`, and `budget.py` parses and validates its own field.

### Ordering

After T-0187 (`board.py` overview) and item B (`run.sh`). Plan level L2.

### Risks

- A budget set too low stops work for no reason. The stop is a question, not a refusal, and `ack` raises it once.
- Duplicate counting across worktrees. Dedupe by `attempt_id`.

### Validation

- Selftest with seeded run records: under 80 percent is `ok`, at 80 `warn` (exit 3), over 100 `over`, a duplicated `attempt_id` counts once, no budget exits 2.
- Negative controls: `run.sh` with a seeded `warn` state and no ack exits 3 before any model call; with an ack it launches; a ticket with no budget launches unchanged.
- Live: seed a ticket at 85 percent and show the conductor's single AskUserQuestion on Claude.

## Build order against existing tickets

| Order | Item | Needs first | Owns (one writer) |
| --- | --- | --- | --- |
| 1 | A spec gate | T-0195, T-0201 | `specgate.py`, `run.sh` plan-reviewer gate, `steps.py` split and review |
| 2 | B handoff freeze | T-0196, T-0199, A | `run_lifecycle.py`, `steps.py` next, resume, review (stale input), hook |
| 3 | C replan delta and checklist | T-0199, T-0200, T-0201, T-0202, A | `steps.py replan-handoff`, `planner.md`, `plan-reviewer.md`, `footprint.py` |
| 4 | D budget | T-0187, T-0199, B | `budget.py`, `run.sh` budget gate, `board.py` column |

`scripts/check.py` and `scripts/check.sh` are appended to by every ticket, including T-0183 to T-0187. Each build merges main in before its local merge and keeps both sides, as T-0185 did.

## Targets

Measured from `runs.jsonl` and `footprint.py`, tentative until ten tickets have run on the new process.

| Measure | Baseline (this week) | Target |
| --- | --- | --- |
| Plans returned `replan` at review | 4 of 7 | 2 of 7 or fewer |
| Planner runs per ticket | 10 over 6 tickets (1.7) | 1.3 or fewer |
| Cost per build ticket (median) | about $22 | $15 or less |
| Plan-review cost per ticket | about $6.80 ($41 over 6 tickets) | $4 or less |
| Mechanical findings reaching a reviewer | 3 of 10 | 0 |

A target is a hypothesis. If the replay in item C shows the checklist catches fewer than half the judgment classes, the delta and checklist change is not worth its text and is removed.

## Open questions for the user

1. Should delta re-reviews run at a lower reviewer effort than a first review? This changes a model or effort default, so it needs your decision. Default: no change.
2. Budget tier defaults: S $5, M $30, L $60. Default as listed; change them if the medians look wrong to you.
3. Should the handoff-edit hook deny the edit or warn? Default: deny, with a message naming the escape.

## Validation of this addendum

An independent architect review of v0.1 is recorded in `../validation/lean-sdlc-cost-control-review.md`.

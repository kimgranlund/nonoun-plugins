# Lean SDLC cost control

Version 0.2, 2026-10-04. Proposal addendum to [the lean design](design.md). Nothing here is built. It adds four items the lean tickets T-0193 to T-0208 do not cover. It changes no model or effort default.

## Problem

Role runs on 2026-10-04 cost about $190 over 78 runs (recounted from every `runs.jsonl` in the repository and its worktrees, deduplicated by `attempt_id`). The cost is concentrated where plans are written and checked, not where code is written.

| Role | Runs | Cost | Share |
| --- | --- | --- | --- |
| planner L3 | 9 | $51 | 27% |
| verifier L3 (branch and release) | 8 | $43 | 22% |
| plan-reviewer | 10 | $41 | 21% |
| builders | 26 | $36 | 19% |
| architect | 2 | $12 | 6% |
| everything else (verifier L1 and L2, planner L1 and L2, filer) | 23 | $8 | 4% |

Counted 2026-10-04 00:00 to 17:32 UTC. Per ticket (build tickets only): T-0203 $14.5, T-0185 $16.7, T-0202 $25.3, T-0197 $23.5, T-0195 $27.6, T-0183 $36.5 (still open). Median about $24.

Verifier L3 is the second line ($43) and no item below touches it; naming the lever is in scope, and the model and effort choice is the user's (open question 1 covers reviewers, not verifiers).

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

A deterministic check that catches the mechanical plan defects before any plan-reviewer runs. Split into A1 (free, ships first) and A2.

### Gap

`lint` is static and never runs anything. Two classes escape it: a criterion that is already green when its step starts (so it cannot detect the step), and a guard that cannot finish inside the default 300-second guard timeout. Both timeout findings this week came from a conductor that never passed `--guard-timeout`, which no skill or agent documents.

### Design

New script `scripts/specgate.py`. It imports `steps` from its own directory for `find_plan`, `parse_steps`, `criteria_lines`, `line_spans` and `guard_spans`, as `board.py` imports `tickets`, so there is one criterion parser. It has no `measure` subcommand and no `slow-commands.json`: the plan carries the fact itself.

- Plan line `guard timeout: <seconds>` (plan level, or in a step block next to `level:`). The planner measures a whole-suite guard once and writes it. `steps.py split --only` reads it as the default for `--guard-timeout`, and `specgate.py check` flags a `(guard)` span that runs `check.sh` (or any command the planner rule names as slow) when the plan has no such line. `agents/planner.md` and `skills/handoff-format/SKILL.md` carry one rule line for it.
- `specgate.py check <plan | task dir>`: static, read-only, exit 0 or 1. Findings: the missing timeout line above; a criterion span repeated verbatim across steps (the second T-0183 step 3 criterion repeated step 2's text); a `(red)` tag beside `(guard)` on one line.
- `(red)` is a new criterion tag next to `(guard)`: a control that must be red now and green after the step. It is opt-in. `steps.py swap` today enforces tag parity for `(guard)` only, so A2 extends that parity to `(red)`.
- `specgate.py red <task dir> --step N [--timeout S]` (A2): runs a step's `(red)` spans in the current tree under the snapshot `steps.py` already takes for guards (`tree_state`, `run_guards`), and refuses a zero exit (`red-first: step <n>: <span> is green now; it cannot detect the change`), a timeout, or a tree change. It runs in the current tree, not a base worktree, because builders never commit, so a base checkout lacks steps 1 to N-1 and would call an earlier step's delivery red. `red --base` is a second form that runs the span in a detached worktree at `$SDLC_BASE_SHA` for the pre-build stage only; its path is `<toplevel>/.worktrees/tmp/specgate-<pid>` (the reaper's prefix rule), because `SDLC_TMP_WORKTREES` is set only inside a role run and the conductor's `split` has none.
- A2 wires `steps.py split --only N` to call `specgate.red` beside its guards, and `steps.py review` and `split` to call `specgate.check`.
- A1 wires `run.sh`: before `exec run_lifecycle.py` (so no `runs.jsonl` line and no `.running` file exist yet), and only for the `plan-reviewer` role, run `specgate.py check "$dir"`. Findings go to stderr and the exit code is 2, the preflight class (1 and 3 already carry other meanings). `SDLC_SPECGATE=off` skips the check and `run.sh` writes `specgate: "off"` on the run line it appends.

### Files

New: `scripts/specgate.py`. Edited: `scripts/run.sh` (A1), `scripts/steps.py` (A2), `agents/planner.md` and `skills/handoff-format/SKILL.md` (timeout line in A1, `(red)` text in A2), `scripts/check.sh`, `scripts/check.py`, `docs/maintenance/sdlc-internals.md`.

### Ordering

T-0195 (`run.sh`) is merged on main. A1 has no unmet dependency and can start now. A2 waits for T-0197, T-0201 (`steps.py`, lint) and T-0202 (`planner.md`), because it edits those files, then owns them until it merges. A1's `planner.md` edit is one line and lands before T-0202 merges only if T-0202 has not touched that section; otherwise A1 waits for T-0202. Plan levels: A1 L2 (no parsed contract changes beyond one plan line), A2 L3.

### Risks

- `red` runs a span with side effects in the current tree. The snapshot refuses after the fact, not before, and a span that writes outside the tree (a cache, a port) is not seen. `red --base` exists for that case and the planner's read-only rule stays the control.
- `(red)` is opt-in. The T-0183 step 3 criteria were untagged, so the tag alone catches nothing from this week; the duplicate-span finding and the split-time run do. A planner rule line (planner.md already requires every new-behavior criterion to be red now) is the control.
- `check.sh` takes 231 s idle and 307 to 417 s under load on this host, so the timeout line must be set from a measurement, not copied.

### Validation

- Positive: a plan with a `guard timeout:` line and a `(red)` control that is red now passes.
- Negative controls, each shown to fail first on the pre-change code or a patched copy: a plan with a `check.sh` guard and no timeout line is refused by `check`; a `(red)` criterion that is green now is refused by `red`; a criterion repeated across steps is refused; `run.sh plan-reviewer` on a failing plan exits 2 before any model call (no `runs.jsonl` line, no `.running`).
- Replay on the four 2026-10 replan findings: `check` must flag the two timeout findings and the duplicate-span finding, and `red` must flag the T-0183 step 3 control once it is tagged. The seven judgment findings must not be flagged. The target is stated as findings caught by `check` before review, not "all three at review".

## B. Handoff freeze

### Gap

Nothing detects that a handoff changed while a role read it. The role finishes, the result is recorded, and it answers an input that no longer exists.

### Design

- `run_lifecycle.py` records `handoff_sha256` in `<role>-<level>.attempt.json` and passes `SDLC_HANDOFF_SHA256` in the child env beside `SDLC_ATTEMPT_ID`. It does not write the run line: `run.sh` appends `runs.jsonl` and `run_lifecycle.py` writes only the attempt record, and `runs.jsonl` is append-only and ordered by line index, so a line is never rewritten.
- `run.sh` rehashes `handoff.md` before its `jq` append and writes `handoff_sha256` and `stale_input: true|false` on the run line, with a stderr line `run.sh: stale input: <handoff> changed while <role> ran`. The role's exit code is unchanged.
- New action class `rerun`. `steps.py next`, `resume` and `review` return `rerun <level> stale input` when the newest result's run line (read through `order.records`) has `stale_input: true`. This is not `invalid result`: that path stops and asks the user, while `rerun` continues automatically with the same role and level and no `## Previous attempt`. `skills/chain/SKILL.md` and the conductor text (T-0199's file, a pointer line only, after T-0199 merges) route it.
- A rerun writes `planner-L3-2.md`, which `review_action`, `lean_warnings` and the footprint `replans` count would read as a replan. Those readers and `footprint.py` exclude a planner result whose run line carries `stale_input: true`. Four copies of one rule: they share one helper in `steps.py`, and `footprint.py` imports it.
- Claude-only hook `hooks/block-handoff-edit.sh`, registered as a new matcher entry `Edit|Write|NotebookEdit` in `adapters/claude/hooks.json` (the registration file; matchers today are Bash, Agent and Monitor, and `run.sh` already disallows `Edit Write NotebookEdit`). It acts in any session, not only role runs, because the conductor's session has no `SDLC_ROLE`. It reads `tool_input.file_path` and denies when the basename is `handoff.md` and a `*.running` file sits beside it, with a message naming the escape. The Edit payload shape is not covered by `hook-live-probe.sh` and gets a live probe. Codex has no hook, so the stale flag is the only cross-host control.
- A change request is a single `change.md` appended in the task dir by the conductor between runs, and the next handoff cites it. The conductor rule is T-0199's text.

### Files

Edited: `scripts/run_lifecycle.py`, `scripts/run.sh`, `scripts/steps.py`, `scripts/footprint.py`, `adapters/claude/hooks.json`, new `hooks/block-handoff-edit.sh`, `scripts/hook-selftest.sh`, `scripts/hook-live-probe.sh`, `docs/maintenance/claude-hooks.md`, `skills/chain/SKILL.md`, `scripts/check.py`, a dated `docs/validation/handoff-freeze-live-run.md`.

### Ordering

After T-0196 (`steps.py next` and `resume`), T-0199 (`conductor.md`, `chain/SKILL.md` batching text), T-0197, A2 and T-0183 (it appends to `check.sh`). Plan level L3.

### Risks

- A legitimate edit during a run. The hook message names `change.md` and the stop-and-wait escape. A `.running` file left by a SIGKILLed run keeps denying until `run_lifecycle.py recover` removes it.
- The stale-exclusion rule has four readers; a missed one makes one stale rerun force a plan review or flip a lean ticket to full. A selftest covers each reader.

### Validation

- A selftest edits `handoff.md` between launch and completion with a stub role: the run line has `stale_input: true` and `steps.py next` returns `rerun`.
- Negative controls: no edit is not flagged; a role that never reads the handoff but whose handoff changed is still flagged (the hash decides); an edit to a sibling file is not flagged; a stale planner rerun does not make `review_action` require a plan review.
- Hook: deny with a `.running` file beside `handoff.md`, allow without it, allow for another file name, and a live probe of the Edit payload.
- Live: one real planner run on Claude and one on Codex with an edit made mid-run ends in `rerun`.

## C. Replan as a delta, and a planner checklist

### Gap

A replan today is a new planning run that rereads the repository. The seven judgment findings above are code-reading defects the first plan missed. Cheaper re-review and a planner that avoids the known classes both reduce the loop.

### Design

1. Replan input. `steps.py replan-handoff <task dir>` is the scripted form of the append the chain already does by hand (`chain/SKILL.md:48`, a `plan review: replan: <finding>` line in `handoff.md`). It writes into `handoff.md`, not a second file, because `read_goal` and the `## Plan review` detection read `handoff.md` only. It refuses when no `replan` verdict counts after the newest plan. The planner already fixes only named steps (planner rule 9); the delta format is T-0200's, and T-0202's carry-forward sections supply research so it is not repeated.
2. Planner checklist, derived from the findings corpus, in `agents/planner.md`: every design row or goal clause has a criterion; every untagged criterion is red at the start of its step; every function the step calls is named with its failure input (no front matter, empty file); every new file is listed in the layout record that enumerates files; a slow guard has a `guard timeout:` line. One line each, each citing a dated finding.
3. Scoped review. `agents/plan-reviewer.md` gains a rule: after `specgate.py check` passes, review only the judgment items (goal coverage, interfaces, hidden dependents) and do not re-verify what the gate checked. A re-review after a delta reads the merged plan view (T-0200's `steps.py resolve`) and the findings it answers.
4. Cap and measure. The existing stop after two `replan` verdicts stays, and the conductor's hard stop on a second replan is T-0199 text (d); this item adds no conductor wording. `footprint.py` gains `replans` (non-stale planner results beyond the first, plus `replan` verdicts), so the target is a gate and not a story.

Running delta re-reviews at a lower effort is a model and effort decision and is left to the user (open question 1). Nothing here changes `run.sh` models or `models.json`.

### Files

Edited: `scripts/steps.py` (`replan-handoff`), `agents/planner.md`, `agents/plan-reviewer.md`, `scripts/footprint.py`, generated Codex agents (`codex_roles.py generate`), `skills/chain/SKILL.md`, `scripts/check.py`.

### Ordering

After T-0199, T-0200 (delta format), T-0201 (anchor rule, `planner.md` and lint), T-0202 (`planner.md`) and A2. `steps.py` and `planner.md` have one writer at a time. Plan level L3.

### Risks

- A checklist that grows. Each line cites a finding in a dated record; a line with no citation after two releases is removed.
- A delta that hides a cross-step effect. T-0200's resolve merges the view and lint runs on the merged plan.

### Validation

- A selftest for `replan-handoff` on a seeded task dir with a `replan` verdict, and a negative control that it refuses without one.
- Replay: use the checklist as a rubric on the original plans of the four replans and count how many findings it names before review; record the count and the misses. If it names fewer than half the judgment findings, the checklist is not worth its text and is removed.
- A `footprint.py` selftest for `replans` on a seeded multi-planner task dir that includes one stale rerun.

## D. Per-ticket cost budget

### Gap

Nothing meters spend. `board.py` sums cost per task for display, but no limit exists and the conductor never sees a number to react to.

### Design

- Front matter `budget_usd: <number>` on a ticket, optional, set at filing. Tier defaults from this week's medians: size S $5, M $30, L $60, XL none (ask). They are defaults the user may change (open question 2).
- New `scripts/budget.py`:
  - `status <ticket dir>` prints `spend`, `budget`, `percent`, `state` (`ok`, `warn` at 80 percent, `over` at 100), and `unmetered_runs: N`. Exit 0 ok, 3 warn or over, 2 no budget set. These exit codes are internal to `budget.py`.
  - `set <ticket> --tier S|M|L` writes the field. `ack <ticket dir> --usd N --reason TEXT` writes `budget-ack.md` raising the ceiling once.
  - `ticket_of(handoff dir)` walks up from a step dir, including `step-<n>.superseded-<k>/step-<n>/`, to the nearest `handoff.md` with front matter, bounded by the `.sdlc` root.
  - Spend is `cost_usd` summed from every `runs.jsonl` under the ticket folder, recursively, deduplicated by `attempt_id`. A null `cost_usd` counts 0 and is reported as unmetered. Codex runs record no cost (`codex_exec.py`), so the meter covers Claude roles only; the entry file says so.
- `run.sh` pre-launch, before `exec run_lifecycle.py`: when the ticket has a budget and `budget.py status` is warn or over with no later `budget-ack.md`, `run.sh` exits 4 with `run.sh: budget <pct>%: ask the user; budget.py ack`. Exit 3 already means "result failed validation" to the conductor, so 4 is used. T-0199's stop rule (d) turns exit 4 into one question to the user. A ticket with no budget is unmetered, so existing repos see no change.
- `board.py` gains a Budget column rendered only when some task's ticket has `budget_usd`, gated like the ID and Ticket columns so the default four-column output is byte-identical (T-0187 requires it unchanged). Its values come from `budget.py status`, because `board.py`'s own cost sum reads one level and would disagree on nested superseded dirs.

Limit: spend covers Claude `run.sh` roles only. Conductor and background agent sessions are not in `runs.jsonl`, so the budget bounds the pipeline, not the session.

### Files

New: `scripts/budget.py`. Edited: `scripts/run.sh` (gate), `scripts/board.py` (column), `skills/ticket/SKILL.md` (set at filing), `scripts/check.sh`, `scripts/check.py`, `docs/maintenance/sdlc-internals.md`. `tickets.py` is not edited: it validates `REQUIRED` and `ENUMS` only, so `budget_usd` passes `check` unvalidated like `claimed_by`, and `budget.py` validates its own field. `agents/conductor.md` is not edited here.

### Ordering

After T-0187 (`board.py`), T-0199 (conductor text) and B (`run.sh`, `run_lifecycle.py`). Plan level L3: the conductor parses `run.sh` exit codes (`conductor.md` exit 3 line), so a new exit code is a parsed contract, and the design's own rule puts L3 where a ticket changes a contract other roles parse.

### Risks

- A budget set too low stops work for no reason. The stop is a question, not a refusal, and `ack` raises it once.
- Concurrent worktrees carry copies of every task dir. A budget computed in one tree after a partial merge double-counts until `attempt_id` dedupe sees both copies, and counts nothing for runs whose copies were never merged.
- If most spend moves to conductor sessions or Codex, the meter reads low and the warning never fires.

### Validation

- A selftest with seeded run records: under 80 percent is `ok`, at 80 `warn` (exit 3), over 100 `over`, a duplicated `attempt_id` counts once, a null cost counts as unmetered, a superseded-dir run counts, no budget exits 2.
- Negative controls: `run.sh` with a seeded `warn` state and no ack exits 4 before any model call; with an ack it launches; a ticket with no budget launches unchanged; the board's default output with no budget set is byte-identical to before.
- Live: seed a ticket at 85 percent and show the single question on Claude.

## Build order against existing tickets

| Order | Item | Needs first | Owns (one writer) | Plan level |
| --- | --- | --- | --- | --- |
| 1 | A1 spec check and `run.sh` gate | none (T-0195 merged) | `specgate.py` (check), `run.sh` gate, plan-timeout line in `steps.py split` default and `planner.md` | L2 |
| 2 | A2 `red` and `(red)` | T-0197, T-0201, T-0202, A1 | `specgate.py` (red), `steps.py` split and review wiring, swap parity, `planner.md` | L3 |
| 3 | B handoff freeze | T-0196, T-0197, T-0199, A2, T-0183 | `run_lifecycle.py`, `run.sh` rehash, `steps.py` next, resume, review, `adapters/claude/hooks.json`, hook | L3 |
| 4 | C replan delta and checklist | T-0199, T-0200, T-0201, T-0202, A2 | `steps.py replan-handoff`, `planner.md`, `plan-reviewer.md`, `footprint.py` | L3 |
| 5 | D budget | T-0187, T-0199, B | `budget.py`, `run.sh` budget gate, `board.py` column | L3 |

`scripts/check.py` and `scripts/check.sh` are appended to by every ticket, including T-0183 to T-0187. Each build merges main in before its local merge and keeps both sides, as T-0185 did.

## Filed tickets

Filed 2026-10-04 as proposed, with `depends` set from the build order: A1 T-0210 (`.sdlc/0210-spec-gate-check`), A2 T-0211, B T-0212, C T-0213, D T-0214. T-0209 (maintainer lean default) is separate and not part of this addendum.

## Targets

Measured from `runs.jsonl` and `footprint.py`, tentative until ten tickets have run on the new process.

| Measure | Baseline (this week) | Target |
| --- | --- | --- |
| Plans returned `replan` at review | 4 of 7 (T-0183 and T-0184 verdicts are dated 2026-10-01, the cost rows are 2026-10-04 only) | 2 of 7 or fewer |
| Planner runs per ticket | 10 over 6 tickets (1.7) | 1.3 or fewer |
| Cost per build ticket (median) | about $24 | $15 or less |
| Plan-review cost per ticket | about $6.80 ($41 over 6 tickets) | $4 or less |
| Mechanical findings reaching a reviewer | 3 of 10 (T-0183 step 3, T-0183 step 7, T-0195 step 4) | 0 for the two timeout findings and the duplicate span; the untagged already-green control needs `(red)` |

A target is a hypothesis. If the replay in item C shows the checklist catches fewer than half the judgment classes, the delta and checklist change is not worth its text and is removed.

## Open questions for the user

1. Should delta re-reviews run at a lower reviewer effort than a first review? This changes a model or effort default, so it needs your decision. Default: no change.
2. Budget tier defaults: S $5, M $30, L $60. Default as listed; change them if the medians look wrong to you.
3. Should the handoff-edit hook deny the edit or warn? Default: deny, with a message naming the escape.

## Validation of this addendum

An independent architect review of v0.1 (verdict ready after fixes, 3 blockers, 18 findings) is recorded in `../validation/lean-sdlc-cost-control-review.md`. v0.2 applies all of them. The v0.2 edits were not re-reviewed; each build ticket is filed as `proposed` and goes through plan review before any build.

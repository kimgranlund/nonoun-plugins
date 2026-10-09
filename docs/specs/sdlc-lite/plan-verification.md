# plan-verification skill

Status: design, approved by the maintainer on 2026-10-09 (build T-0407 filed); implementation in progress in T-0407. Version 0.1, 2026-10-09, ticket T-0405. Decided by the maintainer on 2026-10-09: intent, rubric and KPI capture becomes a new `plan-verification` skill that `plan-goal` uses. The build is a separate ticket (section 8); this ticket writes no skill and changes no script.

## 1. Problem

[plan-goal](../../../plugins/sdlc-lite/skills/plan-goal/SKILL.md) fills five sections: Scope, How to work, Budget and stop rules, Authorization, Done when. Three gaps, all observed in the files:

- No section says what the goal is for. Scope lists tickets; nothing states the outcome they serve or why.
- Done when can be met by closing tickets. `plan_check.py` `done-uncheckable` accepts "a merged ticket" ([goal-rules](../../../plugins/sdlc-lite/skills/plan-goal/references/goal-rules.md), `CHECKABLE`), so a goal can end green with the outcome unmoved.
- plan-goal never reads `docs/goals` or `docs/kpi`, the homes built in 0.22.1 ([goals and KPIs](../repo-onboarding/goals-and-kpi.md), T-0392). Its Gather step reads tickets, lanes and spend only.

## 2. What the skill produces: the outcome block

One block, four parts, in this order. A goal block carries it as the sections below; another caller embeds it the same way.

| Part | Content | Rule |
|---|---|---|
| Outcome | One sentence: the state of the world that means the work succeeded, then `Why:` one sentence on what it protects or buys | Not a ticket list and not a verb about effort ("work on", "improve") |
| Measured by | A KPI id (`K-001`) or a backticked runnable command, then `before: <value>` read by running it now, then `target: <bound>` | A number the reader can reproduce. `before: unmeasured: <reason>` is allowed with a warning. `none: <reason>` replaces the whole line for an outcome that cannot be measured yet |
| Rubric | 3 to 5 numbered criteria, each `<what> | pass: <threshold>` with the file or command that decides it | One criterion is the Measured by threshold itself; the rest cover what the number cannot (no regression, a record exists, scope held) |
| Negative control | One line naming a state in which the measure reads red, and the variable that makes it red | The cheapest control is the `before` value sitting on the wrong side of `target`: the measure is red today and must turn green. Otherwise name a mutation, per [checks-that-bite](../../../plugins/sdlc-lite/skills/checks-that-bite/SKILL.md) |

Example, as it appears inside a goal block:

```
Outcome: every run leaves a cost row. Why: spend and load cannot be sized from unmetered runs.
Measured by: K-001 (`python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d`), before: 8.3, target: <= 5.
Rubric:
1. Unmetered share | pass: the measure reads 5 or below.
2. No regression | pass: check.sh exits 0 on main.
3. Scope held | pass: only T-0001 and T-0002 are closed by this goal.
Negative control: the measure reads 8.3 now, above the target of 5, so it is red before any ticket lands.
```

Procedure, in `skills/plan-verification/SKILL.md`:

1. Gather. When the caller cites a goal id (`G-001`), read that file under `docs/goals/` and take Outcome, Why and Done when from it. Otherwise list `docs/goals/` and `docs/kpi/` with Glob (a repository without them skips this) and use an active goal whose scope matches the thread. Never invent a KPI id.
2. Choose the measure: an existing KPI first (its `measure:`, `read:`, `target:`), then a command the thread names, then ask once. A command that writes, spends or publishes is never run to get a `before` value.
3. Run the measure once for `before`. Show the command and its output line under `Why this plan`.
4. Draft the rubric from the goal's Done when and the tickets' own acceptance criteria. Read them; do not rewrite them.
5. Write the negative control.
6. Missing target or measure: one `AskUserQuestion` round with 2 to 4 reasoned options. Unattended (`SDLC_HEADLESS=1`): never ask; mark each gap as a `warn` line.

The skill checks shape with `plan_check.py goal` through its caller; it writes no file under `docs/` and never creates a goal or KPI file. When no KPI exists for a measure worth keeping, it adds one line to `Why this plan`: `propose K-file for <command>`, left to a ticket.

## 3. What it does not own

| Concern | Owner | Boundary |
|---|---|---|
| Ordered steps and per-step acceptance criteria | [planner](../../../plugins/sdlc-lite/agents/planner.md) | The rubric is goal-level evidence. A planner may read it as input; the skill never writes or edits a step criterion |
| Pass or fail on built work | [verifier](../../../plugins/sdlc-lite/agents/verifier.md) | The rubric states thresholds; nobody is dispatched by the skill. Applying the rubric at the end is the goal's Done when command, or a verifier ticket the scope names. One verifier per ticket stays true |
| Ticket Intent, Do, Non-goals, Done when | handoff and the ticket's `handoff.md` ([handoff-format](../../../plugins/sdlc-lite/skills/handoff-format/SKILL.md)) | The outcome sits above tickets and serves several. A ticket cites it in `## Context` as text (`G-001`) |
| Goal and KPI files | `docs/goals`, `docs/kpi`, checked by `docs_check.py` rules G-1 to G-5 | The skill reads them and writes none |
| Authorization, budget, stop rules, scope list, lane | plan-goal | Unchanged |
| How to write a check that bites | checks-that-bite | The skill links it for the control; it does not restate the bestiary |
| Retro finding score and `outcome metric:` line | [fleet-retro rubric](../../../plugins/sdlc-lite/skills/fleet-retro/rubric.md) | A different rubric (actionability of a finding). The `before:` shape is shared on purpose, so a ticket filed under a goal reads `outcome metric: K-001, before: 8.3` unchanged |

## 4. How plan-goal calls it

plan-goal gains one step between Gather and Write: `## 2. Capture the outcome`. It reads `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/SKILL.md` and follows it, then places the result in the block. Later steps renumber (Write 3, Check 4, Return 5). A skill does not invoke another by name in a way both hosts honor, so the call is a read-and-follow of a plugin-root path, the form the self-contained skill check (check.py item 42) already allows.

Block order becomes: `/goal` line, Scope, Outcome, Measured by, Rubric, Negative control, How to work, Budget and stop rules, Authorization, Done when. The 5000 character cap stays; the example in `goal-rules.md` is rewritten to fit and the capture adds about 700 characters, so a long Scope is trimmed first.

`plan_check.py goal` gains two fail rules. Both are shape checks: the script cannot know a `before` value is true, only that it is present and that the goal ends on it.

| Rule | Fails when | Negative control (a mutant of `GOOD_GOAL` that must be flagged as this rule) |
|---|---|---|
| `outcome-block` | the block lacks an `Outcome` line with a `Why:`; or lacks `Measured by` naming a `K-\d+` id or a backticked command with `before:` and `target:` (or `none: <reason>`); or `Rubric` has fewer than 3 or more than 5 numbered criteria, or a criterion lacks `pass:`; or there is no `Negative control` line | (a) the Outcome line deleted; (b) `Why:` deleted; (c) the Measured by command and K id replaced by "it works"; (d) `before:` deleted; (e) the Rubric cut to 2 criteria; (f) one `pass:` deleted; (g) the Negative control line deleted. Seven mutants, one per clause |
| `done-measured` | `Done when` names neither the Measured by id or command nor a `target`/threshold from it, so closing tickets alone would satisfy it | (a) `GOOD_GOAL` Done when reduced to "T-0001 and T-0002 are closed on main, or the goal stopped on a limit with state written to .sdlc/notes.md", which today passes every rule and must now fail; (b) Done when naming a different K id than Measured by |

Two warnings, not failures: `before-unmeasured` (the `before` value is `unmeasured: <reason>`) and `no-measure` (`Measured by: none: <reason>`). Both mirror `docs_check` G-4's `none: <reason>` escape, so an honest unmeasurable goal is not blocked and is not hidden.

A third check is advice only: when the block cites `K-\d+` and a `docs/kpi/` folder exists under the repository root, `plan_check.py` warns `kpi-unresolved` if no file `docs/kpi/NNN-*.md` matches. The repository root is the parent of `--root` (default `.sdlc`), as `check_fanout` resolves it; the rule does not fail, because a consumer repository may keep KPIs elsewhere.

## 5. Whether the others use it later

| Skill | Decision | Brought back when |
|---|---|---|
| plan-loop | Not in version 1. A loop watches a condition; its stop condition already carries a command | A loop is planned whose stop condition is an outcome threshold rather than a status; it then cites a goal id and the Measured by line only |
| plan-fanout | Not in version 1. Lanes serve tickets; the gate is merge safety, not outcome | A fanout run closes tickets that serve no active goal in two retros; the lane brief then carries the Outcome line |
| ticket | Not in version 1. Tickets cite `G-NNN` in Context, per the goals design; no new front matter field | A ticket serves a goal and its retro cannot find which: add `serves: G-NNN` to the ticket front matter in its own ticket |

The shared reference makes each later use a read of one path and no copy.

## 6. Where the shared reference lives

`plugins/sdlc-lite/skills/plan-verification/references/outcome-block.md` holds the block format, the four parts' rules, the before-value procedure, the control forms and the example above. `SKILL.md` points at it with a relative link; plan-goal's `goal-rules.md` points at it with `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/references/outcome-block.md`; a later skill does the same. One home, no copied table, and it ships with the plugin so it works in a consumer install and on Codex.

## 7. Files the build changes

| File | Change |
|---|---|
| `plugins/sdlc-lite/skills/plan-verification/SKILL.md` | New. Frontmatter, `Codex host` line, the procedure of section 2, an `Unattended` line. `allowed-tools`: Read, Grep, Glob, AskUserQuestion; the `before` run uses the host's normal Bash permission, not a pre-allow |
| `plugins/sdlc-lite/skills/plan-verification/references/outcome-block.md` | New. The shared reference of section 6 |
| `plugins/sdlc-lite/skills/plan-goal/SKILL.md` | New step 2, renumber, Return mentions the outcome lines |
| `plugins/sdlc-lite/skills/plan-goal/references/goal-rules.md` | Three rule rows (outcome, measure, done-measured) and the rewritten example |
| `plugins/sdlc-lite/scripts/plan_check.py` | `outcome-block` and `done-measured`, the two warnings, the `kpi-unresolved` advice, `GOOD_GOAL` rewritten, the nine mutants as selftest cases |
| `plugins/sdlc-lite/scripts/check.py` | New item 48 and its docstring entry: plan-verification names `references/outcome-block.md`; plan-goal names `plan-verification`; no `harness:` reference; routed from the entry skill; each phrase removed is flagged. Item 31 stays for the three block-returning skills |
| `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md` | One routing row: capture an outcome, rubric and KPI before a plan, to plan-verification |
| `docs/README.md` | One row for this design, then marked built |
| `docs/specs/sdlc-lite/README.md` and the managed block of `docs/specs/sdlc-lite/AGENTS.md` | List this document; regenerate the block with `onboard.py` rather than hand edit |
| `docs/specs/sdlc-lite/plan-verification.md` | The status line moves from design to built, with the build commit |

Not changed: models and efforts, `docs_check.py`, the role agents, `tickets.py`, the fanout and loop skills, any version number (the release owner bumps it).

## 8. The build as its own ticket

Type feature, size L2 (about ten files, one new mechanism, a script rule with controls), `depends: [T-0405]`, filed after this design is reviewed. Its criteria:

1. `(red)` Before the change, the mutant "Outcome, Measured by, Rubric and Negative control deleted" passes `check_goal`; after, it is flagged `outcome-block`. Run through `specgate.py red`.
2. `(red)` Before, a Done when that only closes tickets passes; after, it is flagged `done-measured`.
3. `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0, and each of the nine mutants of section 4 is flagged as its rule (the observed negative control the repository rules require for a new gate).
4. `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`, and `bash plugins/sdlc-lite/scripts/check.sh` exit 0.
5. Live: `/plan-goal` run in a throwaway project returns a block that passes `plan_check.py goal`, with a `before` value read from a real run. Recorded in a dated report beside [the plan skills live run](../../reports/plan-skills-live-run.md). If it cannot run, the ticket reports it as unverified.

Migration for existing goals: a goal already pasted into `/goal` is unchanged, because the stop hook holds the pasted text and `plan_check.py` runs only when a block is planned. Goal blocks recorded in reports are history. Re-planning an old goal fails the two new rules until it gains the block; that is the intended pressure. No `--legacy` switch is added: the sanctioned way out is `Measured by: none: <reason>`, which passes with a warning and leaves the gap visible. The example in `goal-rules.md` and `GOOD_GOAL` are rewritten in the same change.

## 9. Rejected alternatives

- Extend plan-goal only. Cheapest, and rejected: plan-loop, plan-fanout and later callers would copy the capture or go without; the capture needs its own reads (`docs/goals`, `docs/kpi`) and its own boundaries, which would push plan-goal past the size where its five-section Return is easy to hold; and check.py item 31 fixes the phrase set of every plan skill, so a capture procedure inside plan-goal couples two concerns that change at different rates. The cost of the separate skill is one more read for plan-goal.
- Tickets only: put Outcome, KPI and rubric in each handoff's Intent. Rejected: one outcome spans several tickets, so the KPI would be copied or split; a ticket closes on its own done criterion, which is exactly the gap (done without the outcome moving); and the `/goal` stop hook reads the pasted block, not ticket files, so the stop condition would still not name the measure.
- A new role or agent that scores the outcome. Rejected: it adds a dispatch and a model seat for doubt the evidence does not show; the rubric is applied by the Done when command or a verifier ticket the scope already names.
- Fail goals whose `before` value was not run by the skill. Rejected for now: the script cannot tell. The value and its command are shown under `Why this plan`, where a reader checks them.

## 10. Risks and limits

- The new rules check shape. A goal can pass with a weak rubric or a `before` value typed by hand. The defense is the shown command line and the verifier ticket, not the script.
- The block grows by about 700 characters against a 5000 character cap. If goals hit `too-long` often, raise the cap in the build ticket's follow-up, not here.
- Codex: `/goal` behavior is unverified on Codex (plan-goal already says so); the capture is host-neutral text and is carried as is.
- Evidence labels: the three gaps in section 1 are observed in the named files; the 700 character figure and the L2 size are estimates, not measured.

# Outcome block

Evidence labels: observed here (a file of this repo), from the code (`scripts/plan_check.py`), or inferred.

The block is four parts, in this order. A `/goal` block carries them between Scope and How to work; another plan skill embeds them the same way.

| Part | Content | Rule |
|---|---|---|
| Outcome | One sentence: the state of the world that means the work succeeded, then `Why:` one sentence on what it protects or buys | Not a ticket list and not a verb about effort ("work on", "improve") |
| Measured by | A KPI id (`K-001`) or a backticked runnable command, then `before: <value>` read by running it now, then `target: <bound>` | A number the reader can reproduce. `before: unmeasured: <reason>` is allowed with a warning. `none: <reason>` replaces the whole line for an outcome that cannot be measured yet |
| Rubric | 3 to 5 numbered criteria, each `<what> | pass: <threshold>` with the file or command that decides it | One criterion is the Measured by threshold itself; the rest cover what the number cannot (no regression, a record exists, scope held) |
| Negative control | One line naming a state in which the measure reads red, and the variable that makes it red | The cheapest control is the `before` value sitting on the wrong side of `target`: the measure is red today and must turn green. Otherwise name a mutation, per the checks-that-bite skill |

## What the check enforces

`plan_check.py goal` runs two fail rules and three warnings. They check shape: the script cannot know a `before` value is true, only that it is present and that the goal ends on it.

| Finding | When |
|---|---|
| FAIL outcome-block | No `Outcome` line with a `Why:`; no `Measured by` naming a `K-\d+` id or a backticked command with `before:` and `target:` (or `none: <reason>`); a Rubric with fewer than 3 or more than 5 numbered criteria, or a criterion without `pass:`; no `Negative control` line |
| FAIL done-measured | `Done when` names neither the Measured by id or command nor its target, so closing tickets alone would satisfy it |
| warn before-unmeasured | The `before` value is `unmeasured: <reason>` |
| warn no-measure | `Measured by: none: <reason>` |
| warn kpi-unresolved | The block cites `K-NNN` and the repository keeps a `docs/kpi/` folder with no `NNN-*.md` file (the repository root is the parent of `--root`) |

## The before value

Run the measure once, now, and show the command and its output line under `Why this plan`. A command that writes, spends, or publishes is never run for this; use `before: unmeasured: <reason>`.

## Example, as it appears inside a goal block

```
Outcome: every run leaves a cost row. Why: spend and load cannot be sized from unmetered runs.
Measured by: K-001 (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fleet_collect.py collect . --since 7d`), before: 8.3, target: <= 5.
Rubric:
1. Unmetered share | pass: the measure reads 5 or below.
2. No regression | pass: check.sh exits 0 on main.
3. Scope held | pass: only T-0001 and T-0002 are closed by this goal.
Negative control: the measure reads 8.3 now, above the target of 5, so it is red before any ticket lands.
```

The goal's `Done when` then names the measure (`K-001`, its command, or its target), so closing tickets alone cannot end the goal.

## Boundaries

The planner owns step criteria; the verifier owns pass or fail on built work; the ticket's `handoff.md` owns its own Intent and Done when. A ticket cites the goal in `## Context` as text (`G-001`). Applying the rubric at the end is the goal's Done when command, or a verifier ticket the scope names.

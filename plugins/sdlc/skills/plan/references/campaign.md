# Campaign rules

Evidence labels: observed here (a gen-ui-kit campaign, 2026-10-09, as briefed by its factory), from the code (`scripts/plan_check.py campaign`), or inferred.
- Gather (a campaign is a migration where a shared tool and a blocking gate land before N parallel lanes run): the outcome in one sentence; a census command that counts the units still to migrate (exit 0, prints a number), found in the repo or built by Wave 0, and no plan without one; the existing gates and how a new gate joins the gate chain (`gate-classes.json` or the equivalent); machine load (`uptime`) and the lane caps.
- Ask once, with 2 to 4 reasoned options each: the spend cap, the GitHub rights (push, PR, merge), and the lane cap.
- Write the plan from the template below in wave order: Wave 0, Wave 1 with a partition generated from the census and printed as the lane, directory, units table, Wave 2, Wave 3, then one `/goal` block per [the goal rules](goal.md). When the owner says "no limits", set a dollar backstop from the budget level times the lane count and call it a backstop.
- Check and return: pipe the whole plan, the lines above the fence plus the fenced `/goal` block, to the campaign lint; return the plan (census, dependency order, lane cap, the four waves, the partition table, the stop rules, done when) before the block. `Why this plan` covers the census, the partition, the cap and the gate; `You must authorize` names spend, push, PRs and merge.

## The check

`plan_check.py campaign` reads the plan from stdin, `--text`, or `--file`. The `/goal` block is the fenced block that starts with `/goal`; it must also pass `plan_check.py goal` (including the outcome block from plan-verification), and its findings print as `goal-<rule>`.

| Finding | Rule |
|---|---|
| FAIL no-census | A `Census:` line with a backticked command that counts the units still to migrate |
| FAIL no-wave0-gate | A Wave 0 section that lands a shared tool and a gate |
| FAIL done-not-command | `Done when:` is a backticked command that exits 0 on main |
| FAIL overlap | Two partition rows name the same directory or one inside the other |
| FAIL no-partition, no-lane-cap | A `| lane | directory | units |` table and a `Lane cap: N` line |
| FAIL lane-cap | More lanes than the cap and no `Cap reason:` line |
| FAIL no-dollar-stop | A `Stop rules:` line with a dollar number |
| FAIL pr-unbounded | Wave 3 gives a PR count, a number or a range like 8 to 10 |
| FAIL no-order | `Dependency order:` says Wave 0 lands on main before any Wave 1 lane starts |
| FAIL no-goal-block | One fenced `/goal` block |
| warn no-allowlist, no-reference-pr, hedge, verb, rfc2119 | Wave 0 has no day-one allowlist; no `Reference PR:` line; the `Campaign:` line or the goal block breaks the controlled-language rules of the plan rules |
| warn machine-load | Load average above half the CPU count and a lane cap above the CPUs left free |
| warn ticket-root | `--root` is not a `.sdlc` folder and holds 0 tickets |

## Template (once every `<placeholder>` is filled, it passes `plan_check.py campaign`)

```
Campaign: <the outcome in one sentence>

Census: `<command>` exits 0 and prints the units still to migrate (<count at planning time>)
Dependency order: Wave 0 lands on main before any Wave 1 lane starts; Wave 2 starts when every Wave 1 lane is merged; Wave 3 starts when Wave 2 passes.
Lane cap: <N>
Cap reason: <only when the partition has more lanes than the cap: why, and who authorized it>

Wave 0 (one lane, lands first): <shared tool> and a blocking gate `<gate command>`, wired into the existing gate chain with no new CI job. The gate starts green through a day-one allowlist of current violators, each with a justification string; a stale entry fails the gate.
Wave 1 (<N> lanes, file-disjoint, one writer per file): each lane migrates its units and deletes its own allowlist entries.
Reference PR: <#number> (the pattern every lane copies)

| lane | directory | units |
|---|---|---|
| a01 | <directory> | <count> |

Wave 2 (bulk review): one verifier per bundle of 5 to 10 lanes on a different model family than the builders, plus a probe sweep with before and after numbers per unit (say dev server or dist).
Wave 3 (bulk PRs): one integration branch per area, <8 to 10> PRs, one plain push each.

Stop rules: stop and write state to <notes file> at $<total> total, $<per lane> per lane, a rate or weekly limit, or three 529s in a row.
Done when: `<gate command>` exits 0 on main with an empty allowlist

<a fenced /goal block, as in the goal rules: Scope, the outcome lines (Outcome, Measured by, Rubric, Negative control), How to work, Budget and stop rules, Authorization, Done when>
```

Worked example (observed): the goal was "granular dependency loading is the standard for every page". 136 html files linked a 120-sheet `components.css`; 22 linked a 348 KB `themes.css`. Wave 0 was one lane building a derivation tool and a blocking gate with a day-one allowlist; Wave 1 was up to 50 file-disjoint lanes migrating pages; Wave 2 was bulk verifier review plus a probe sweep; Wave 3 was 8 to 10 bulk PRs. It was done when the gate exited 0 on main with an empty allowlist.

## Lessons

| Lesson | Label |
|---|---|
| Put the cheapest, highest-signal checks first in the gate chain. The consumer type check ran after 33 gates and cost a whole extra cut run | observed: gen-ui-kit |
| Lane agents commit early (WIP commits) so the factory can restart a crashed lane in the same worktree. The block-role-spawn hook accepts only the dispatch name prepared for that worktree, so a restart reuses the name | observed: gen-ui-kit |
| Dev server and dist behave differently (vite inlines the barrel). A probe that measures requests says which serving mode it used | observed: gen-ui-kit |
| For bulk PRs, edit the PR body, not a label, to retrigger the PR gate | observed: gen-ui-kit |
| The allowlist is a shared file. Lanes delete only their own entries, one entry per line, so the merges stay mechanical; a stale entry fails the gate, which makes "done" a command | observed: gen-ui-kit |
| A new gate adds no CI job, step, or required check; it joins the existing gate chain | observed: gen-ui-kit |
| Lane caps: 4 lanes by default, above 16 needs `--yes-many`; check `uptime` first. A cap above what the machine can run only queues work | from the code: `fanout.py`; inferred |
| Spend: `budget.py` levels L1 $5, L2 $30, L3 $60. When the owner says "no limits", still write a dollar backstop (level times lane count) and call it a backstop | from the code: `budget.py` |
| Publish, tag, and deploy are never implied; name the pushes the plan needs | root `AGENTS.md` shared invariants |

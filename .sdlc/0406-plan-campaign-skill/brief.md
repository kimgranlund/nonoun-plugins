# Brief: a `plan-campaign` skill for sdlc-lite

From the gen-ui-kit conductor, 2026-10-09. Build request for sdlc-lite-author.

## Why
`plan-goal` writes one `/goal` block. `plan-fanout` writes one fanout command. Neither plans a multi-wave migration where a shared tool and gate must land before N parallel lanes run, then bulk review and bulk PRs. We did exactly that by hand in gen-ui-kit and the pieces were reusable. This skill makes it repeatable.

Worked example (observed): goal "granular dependency loading is the standard for every page". 136 html files linked a 120-sheet `components.css`, 22 linked a 348 KB `themes.css`. Plan: Wave 0 one lane builds a derivation tool plus a blocking gate with a day-one allowlist; Wave 1 up to 50 file-disjoint lanes migrate pages and delete their own allowlist entries; Wave 2 bulk verifier review plus a probe sweep; Wave 3 8 to 10 bulk PRs. Done when the gate exits 0 on main with an empty allowlist.

## Name and description
`plan-campaign`. Description: Plan a wave-based campaign (build the tool and gate, migrate N units in parallel lanes, bulk review, bulk PRs) and return one /goal block plus a lane partition. NOT for a single goal (plan-goal), one fanout run (plan-fanout), or running anything.

## Inputs (gather from the repo first, ask once for the rest)
1. The outcome in one sentence.
2. A census command that counts units still to migrate (exit 0, prints a number). Refuse to plan without one.
3. The existing gates and how a new gate is wired into the gate chain (gate-classes.json or equivalent). A new gate must not add a CI job, step or required check.
4. Machine load (`uptime`) and the plugin lane caps.
5. One AskUserQuestion round with reasoned options: spend cap, GitHub rights (push, PR, merge), lane cap.

## Output, in this order
1. Wave 0, one lane, lands first: the shared tool and a blocking gate. The gate starts green via a day-one allowlist of current violators, each with a justification string. A lane deletes its own entries when it migrates; a stale entry fails the gate. This makes "done" a command.
2. Wave 1, N lanes: a directory partition generated from the census, file-disjoint, one writer per file, naming one reference PR as the pattern. Print the partition as a table (lane, directory, unit count).
3. Wave 2, bulk review: one verifier per bundle of 5 to 10 lanes on a different model family than the builders, plus a probe sweep with before and after numbers per unit.
4. Wave 3, bulk PRs: one integration branch per area, a target PR count (8 to 10), one plain push each.
5. A `/goal` block that passes `plan_check.py goal`, with Authorization explicit (publish, tag, deploy never implied) and a dollar backstop when the owner says "no limits" (derive it from budget.py level times lane count and say it is a backstop).

## New check: `plan_check.py campaign`
FAIL when: no Wave 0 gate; done-when is not a command exit code on main; partition has overlapping files; lane count exceeds the cap with no stated reason; no stop rule with a dollar number; PR count unbounded; no stated dependency order (tool lands before lanes start). WARN when: lane cap exceeds what the machine can run (load average above half the CPU count); no reference PR; the ticket root differs from `.sdlc` and `tickets.py check` reports 0 tickets.

## Lessons to bake in (all observed in gen-ui-kit)
- Put the cheapest, highest-signal checks first. The consumer type check ran after 33 gates and cost a whole extra cut run.
- Lane agents must commit early (WIP commits) and the conductor must be able to restart a crashed lane in the same worktree; the block-role-spawn hook only accepts the dispatch name prepared for that worktree, so the restart reuses the name.
- Dev server and dist behave differently (vite inlines the barrel); a probe that measures requests must say which serving mode it used.
- Bulk PRs: edit the PR body, not a label, to retrigger the PR gate.

## Smallest useful v1
The campaign template plus the partition check (file-disjoint, caps, order). The rest can follow.

## Acceptance
`plan_check.py campaign` passes on a block for the page-CSS example above and fails on each FAIL case; a selftest covers each. No em dashes. Build it in the sdlc-lite repo only; do not edit gen-ui-kit.

---
id: T-0039
title: "A defined name for superseded step dirs"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A step replaced by a replan has a defined dir name that board.py and the scripts treat as superseded, not as another step.

## Intent
Literal ask: a step replaced by a replan has a defined dir name that board.py and the scripts treat as superseded, not as another step.
Deltas:
- Exact name: defaulted: `step-<n>.superseded-<k>/` (k = 1, 2, ... the first free number), as the reporter suggested. A live step dir matches exactly `step-<digits>`; anything else under `step-*` is not a live step.
- Board behavior (skip vs show): defaulted: skip. Superseded dirs never render as step rows and never count in step totals or %; the replacement `step-<n>/` is the row.
- Who renames: defaulted: /chain step 4.2 (the conductor, in session), before rewriting step handoffs after a replan: move each `step-<n>/` for n >= the blocked step that already has builder/verifier output to `step-<n>.superseded-<k>/`, then write fresh `step-<n>/handoff.md`.
- Cost and history: defaulted: superseded dirs still count for cost (bench-summary cost, runs.jsonl sums) because that money was spent, but not for steps, passed, or builder attempts of live steps. `has_step_work` may keep counting them (recorded work).
- ⚠ L5 flag in `board.py --summary`: defaulted: only live step dirs count.
- Other `step-*` readers: defaulted: every glob of `step-*` in plugins/sdlc-lite (scripts, skills, agents, bench) is audited and made to skip superseded dirs where it counts steps; statusline.sh's `step-[0-9]*` match of a running role is fine if it still names the step number.
Do: define the name in skills/handoff-format/SKILL.md (layout block plus one rule line); make /chain step 4.2 perform the rename; make board.py (plan_steps, summary L5 check, and any other step glob) and scripts/bench-summary.sh (steps/passed/attempts loop) ignore superseded dirs while bench-summary cost still includes them; add a board.py selftest case where a task has `step-1/`, `step-2/`, and `step-2.superseded-1/` and the board shows exactly two step rows; audit remaining `step-*` globs.
Non-goals: changing how the planner numbers replan steps; changing run.sh output naming (T-0038 did that); migrating existing hand-renamed dirs like `step-15-blocked` (they will simply stop rendering, since they do not match `step-<digits>`).
Done when: board.py selftest includes the superseded case and passes; a manual board render of a task with a superseded dir shows no extra row; bench-summary on a results dir with a superseded dir counts only live steps; scripts/check.sh passes; handoff-format and chain document the name.

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. /chain says to replan and continue from the blocked step but defines no convention for the old step dir. Renaming it step-15-blocked made board.py (which globs step-*) render a second "15." row, and loops that use `ls step-*` counted an extra step. Suggested: a reserved name such as step-<n>.superseded-<k>/ that board.py skips or shows as superseded, and /chain documents it. Pairs with the replan-overwrites-plan ticket.

## Constraints
None beyond the Non-goals. Existing board.py and tickets selftests keep passing.

## Paths (added by the conductor)
All code to change is in this worktree: plugins/sdlc-lite/ (scripts/board.py plan_steps ~line 107 and summary ~line 170 plus selftest, scripts/bench-summary.sh line 13, skills/chain/SKILL.md step 4.2, skills/handoff-format/SKILL.md layout). Check with plugins/sdlc-lite/scripts/check.sh and `python3 plugins/sdlc-lite/scripts/board.py selftest`. Roles are launched by a different checkout's run.sh (/Users/kimba/Projects/nonoun/sdlc-agents); edit only files in this worktree.

---
id: T-0059
title: "Standard merge-branch step template for builders"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Merging two lanes is a standard builder step with criteria it can meet.

## Intent
Literal ask: a `merge <branch>` step template with criteria: no conflict markers, gates green, two-parent commit.
Deltas:
- Where the template lives: defaulted: in the plugin's planner guidance (`agents/planner.md`) and documented in `skills/handoff-format/SKILL.md` next to the step handoff layout, so the planner emits a standard merge step block that `steps.py split` copies like any other step; no new command.
- Who makes the merge commit: defaulted: the builder runs `git merge --no-ff <branch>`, resolves conflicts, and creates the merge commit; this is the one step kind where the builder commits. `agents/builder.md` says so explicitly. Push, PR, and publishing stay blocked (hook unchanged). The verifier still never changes git state.
- Why the peer's builder blocked: the criteria were unmeetable as written. Defaulted: each criterion must be a command that is red before the merge and green after it, checkable by the verifier without changing git state, e.g. HEAD has exactly two parents (`test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`), `<branch>` is an ancestor of HEAD (`git merge-base --is-ancestor <branch> HEAD`), no conflict markers in tracked files (`! git grep -nE '^(<<<<<<<|>>>>>>>)( |$)'` or equivalent scoped to files the merge touched), and the project's gates green, scoped to no new findings versus the first parent when the base is already red.
- gap: which "gates" a target project has; default: the planner names the project's own check/test commands in the step, as it does for any step.
Do: add a standard merge step template (Do and acceptance criteria with meetable, parseable commands) to planner guidance and handoff-format docs; add the builder rule allowing the merge commit on a merge step; keep `steps.py lint` passing on the template's criteria; update CLAUDE.md and `.claude/agents/sdlc-lite-author.md` if they describe these records.
Non-goals: a new script or subcommand; auto-detecting lanes; pushing or publishing; changing run.sh levels or the hook.
Done when: `agents/planner.md` and `skills/handoff-format/SKILL.md` carry the merge step template; `agents/builder.md` permits the merge commit only on a merge step; a plan containing the template step passes `steps.py lint`; `scripts/check.sh` passes with no new failures versus the base commit.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

A merge conflict between lanes needed a hand-written handoff, and the builder correctly blocked on an unmeetable criterion. Suggested: a `merge <branch>` step template with criteria: no conflict markers, gates green, two-parent commit.

## Constraints
What must not change. "None" if none.

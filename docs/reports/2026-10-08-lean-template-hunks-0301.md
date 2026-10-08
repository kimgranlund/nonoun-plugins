# Lean-template hunks from maison T-0301, assessed against 0.22.x

Recorded: 2026-10-08, ticket T-0385. Input: the Codex RCA review in maison `.sdlc/tickets/0301-lean-template-bootstrap-design/` (`proposed-diff.md`, `review-notes.md`), written against 0.21.3. Observed cause stated there: one-line amendments repeated `npm ci`, generated fanout briefs ask for all named checks after any fix, and the planner treats every one-step plan as gates green.

This record states only what a committed file or a command run for it shows. No Codex host behavior was run live; every Codex-facing change below is unverified on that host and is checked only by `codex_roles.py generate --check` parity. The install-receipt integrity check and the T-0299 preflight are proposals in the maison review, not built, and nothing here claims them.

## Disposition per hunk

| Hunk | Disposition | Where |
|---|---|---|
| handoff-format step template, "Validation scope" line | adapt | `agents/planner.md` (the step `### Do` description) and a sentence in `skills/handoff-format/SKILL.md` |
| planner rule 1, probe on the current tree | adapt, in part declined | `agents/planner.md` rule 1 |
| planner rule 14, one-step plans and whole-suite timing | adapt | `agents/planner.md` rule 14 and its timeout bullet |
| fanout.py rerun-all solo briefs | adapt, plus `agents/solo.md` | `scripts/fanout.py` (both briefs), `agents/solo.md` step 3 |
| standing-orders note and lane bootstrap text | decline | stays maison's |

### 1. Validation scope in the step template: adapt

The proposal inserts a literal sentence into the template after `### Do`. That line names maison things (the project bootstrap rule, generated artifacts, the dispatch base and prerequisite tip), and a literal line in a template is copied into every step. Adapted: the planner's `### Do` description now asks for a validation scope (affected behavior and named dependents with the search that found them, tests named by stable title and file rather than by source line, and the integration gate that owns broad coverage when the handoff assigns one). `handoff-format` mirrors it in one sentence. Declined parts: "reuse the project bootstrap rule by link" (plugin text cannot know a project's rule; the project's own AGENTS.md carries it) and "record the actual execution worktree, base and prerequisite tip" (`SDLC_BASE_SHA` and the step dir's `base-sha` already record the base).

### 2. Planner rule 1: adapt, in part declined

Accepted: the rule now says a selection that can come up empty (a title or name filter) also requires a nonzero selected-test count, and that the planner does not run a broad suite, install, generation or browser just to write the plan; the owning step runs it. Declined: rewriting the whole rule. "Reuse a recorded probe" has no probe record in 0.22.x to bind to, so it would be an unenforceable promise. Dropping the dry-run of every `(guard)` at the base commit would remove a resilience control (guards diff against the base, and `steps.py split --only` is the only later catch), so it stays. "Shell negation must not turn a tool error into success" duplicates rule 7's negative-check bullet, rule 11 and `checks-that-bite`, so it is not added again.

### 3. Planner rule 14: adapt

Accepted: a one-step plan is still the gates green step by default, unless the handoff assigns the broad gate to a named integration gate that runs after the lane (for example the `fanout.py land` gates). Then the step proves its affected behavior and named dependents with focused commands and its Do names the gate that owns the rest. The `gates green` title text that `steps.py` reads for step level stays. For the `guard timeout:` line, the value now comes from a completed run of the same command already on record, with a plan-time timing only when no record exists, and never from a run that hit its timeout. Declined: "derive from completed measurements ... record a conservative proposed bound and the uncertainty", because `specgate.py check` only requires the line and the extra uncertainty record has no consumer.

### 4. fanout.py rerun-all briefs: adapt, and `agents/solo.md` changes with it

The brief and the role file must not disagree, so `SOLO_PROMPT`, `SOLO_SUBAGENT_PROMPT` and `agents/solo.md` step 3 now say: after a fix, rerun the checks that fix can affect (every check when unsure), keeping any `(red)` control. This keeps the pillar-quality default for an unsure solo and removes the unconditional repeat. Declined: "within the assigned lane scope", since the ticket itself names the checks and the scope. Generated copies (`solo-L1..L3`, the three Codex solo TOMLs) are regenerated; the planner copies likewise.

### 5. Standing-orders note: decline

The panda bootstrap, `npm ci` reuse receipt text, browser budget and integration order are maison's repo conductor policy (`standing-orders.md`), not plugin text. The receipt checker is unbuilt, so maison keeps recording the actual evidence and does not claim automated verification.

## The eight review cases

| Case | Plugin behavior? | Coverage |
|---|---|---|
| 1 one-file YAML rework, no reinstall | project policy | none here |
| 2 shared token change, dependents by search | rule exists (Contract dependents) | existing planner text; the validation-scope wording is pinned |
| 3 empty selection fails, negation error | partly | `selected-test count` pinned in planner.md; `fanout.py` `VACUOUS_GATE` already covers a vacuous gate (existing fanout selftest) |
| 4 red control stays red then green | yes | existing `specgate.py red` and `steps.py split --only` selftests; the solo brief now keeps any `(red)` control |
| 5 gate result with changed inputs | project policy | none here |
| 6 fresh candidate install, shared node_modules | project policy | none here |
| 7 browser concurrency vs lane cap | project policy (T-0300, T-0386) | none here |
| 8 stale patch after captured hash | handled by this rebase | each hunk above was re-read against current text |

## Checks

`check.py` item 46 pins the accepted text in `agents/planner.md`, `skills/handoff-format/SKILL.md`, `agents/solo.md` and `scripts/fanout.py`, with a negative control per phrase and for a planted old "rerun them all" or "rerun all checks". Run against an export of the pre-change tree, the new item failed for every accepted phrase and for both old rerun-all wordings, and passes on the changed tree. Parser and lint compatibility: the edits are prose in `### Do` descriptions and rule text; no criterion span, step title or lint pattern changed, and the `steps.py`, `fanout.py` and `specgate.py` selftests pass.

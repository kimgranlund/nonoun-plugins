# Verifier reports unmet dependency and deferred-to-owner apart from fail

Status: design, approved by the maintainer on 2026-10-09 ("fold those into 0.22.2"); built by T-0408 (2026-10-09) except two points listed under section 10. Version 0.2, ticket T-0400. Targets 0.22.2.

## 1. Answer in one paragraph

A criterion can be in four states, not two: `pass`, `fail`, `unmet-dependency <subject>` (its check cannot run because a declared prerequisite is not met yet), and `deferred <owner>` (a later stage owns it). The handoff declares which criteria may be held and why, in an optional bracket suffix on the criterion line; the verifier may only hold a declared criterion, and `steps.py` re-derives the claim from the handoff and the dependency state instead of trusting the report. The overall Verdict keeps the values the runner already parses (`pass`, `fail`, `inherited red: <tests>`): it is `pass` only when every criterion is `pass`, so a held criterion always makes it `fail`, and the first line of `## For the next attempt` (`unmet-dependency:` or `deferred:`) tells `steps.py next` this fail is not a defect to rebuild. A new read-only `steps.py open` lists held criteria; `tickets.py close` refuses while any is open, and the owner stage closes one by passing it in a later verifier result.

## 2. Sources

- The evidence: maison 2026-10-09, 11 component lanes where rows 7 to 12 of the component-request template are integration or testing owned and failed in every lane build, and one lane failed on merge order (T-0307 schema). Read as data from `.sdlc/tickets/0301-lean-template-bootstrap-design/codex-progress-bar-stage-evidence.md` in that repository (not present in this tree; unverified here beyond the ticket's `## Context`).
- This repo: [results.py](../../../plugins/sdlc-lite/scripts/results.py) (`SCHEMA`, `_check`, `key_value`, `selftest`, `_steps_cases`), [verifier.md](../../../plugins/sdlc-lite/agents/verifier.md), [handoff-format](../../../plugins/sdlc-lite/skills/handoff-format/SKILL.md), [steps.py](../../../plugins/sdlc-lite/scripts/steps.py) (`next_action` line 1917, `criteria_lines` line 524, `leading_tags` line 594, `batch_verified`, `swap`, `resume_action`), [tickets.py](../../../plugins/sdlc-lite/scripts/tickets.py) (`dep_kind` line 939, `cmd_close` line 1757), and `merge_class` in steps.py with its two callers in [fanout.py](../../../plugins/sdlc-lite/scripts/fanout.py).
- Facts read in the code that shape the design: `results.key_value` fullmatches `pass`, `fail` or `inherited red: .+`, so any other Verdict text is "no verdict" and `next_action` reruns the verifier (twice, then stops); `## Criteria` lines are not parsed by any script today; `tickets.py close` does not read any verifier result (only skips, filer warnings and outside refs); `leading_tags` only accepts `\(\w[\w-]*\)` tags, so a tag with a value does not parse.

## 3. The four states

| State | Meaning | Who may report it | Routed by `steps.py next` as |
|---|---|---|---|
| `pass` | The check ran and holds | verifier | counts toward done |
| `fail` | The check ran and does not hold, or could not run for a reason the work owns | verifier | the existing path: rebuild, bump, replan, stop |
| `unmet-dependency <subject>` | The check cannot run or cannot pass until `<subject>` exists | verifier, only for a subject the handoff declared with `needs:` that is unmet now | `wait`, never a rebuild, bump or replan |
| `deferred <owner>` | The check belongs to a later stage or owner | verifier, only for an owner the handoff declared with `owner:` whose check is not green now | `deferred`, never a rebuild, bump or replan |

`<subject>` uses the grammar `tickets.py dep_kind` already parses for `depends:`: `T-NNNN`, `file:<path>`, `cap:<name>`. `<owner>` is a stage word (lowercase kebab, for example `integration`, `testing`, `merge`) or a `T-NNNN` ticket id.

A declared owner never skips a passing check: if the check is green now, the criterion is `pass`. A hold is allowed only when the check fails or cannot run. This keeps the declaration from hiding a defect that is present now.

## 4. Declaring a held criterion in the handoff

A criterion line may end with one bracket clause, outside any code span:

```
- `test -s out/report.json` [stage: integration; owner: integration]
- `node --test test/schema.test.js` [needs: T-0307, file:schema/progress.json]
```

Keys: `stage` (the stage that normally checks it, informational), `owner` (a stage word or `T-NNNN`; makes the criterion deferrable), `needs` (comma separated subjects; makes it unmet-dependency eligible). Any unknown key, an empty value, or a malformed owner or subject is a `steps.py lint` refusal ending in the `plan defect:` line. A line with no clause behaves as today. The planner or the ticket author writes the clause; a template that knows its rows 7 to 12 are integration owned (the Maison template) writes `[owner: integration]` on them.

Criterion reference: `<step dir name>#<k>` for the k-th line in that step's `### Acceptance criteria` (1-based, over `criteria_lines`), and `ticket#<k>` for the k-th line of a task handoff's `## Acceptance criteria` (the solo lane, where there is no step dir). A `steps.py swap` keeps the ordinal; it must also keep the bracket clause unchanged, or it refuses.

## 5. Exact changes

### 5.1 results.py

- `SCHEMA['verifier']` stays as is: same key, same allowed tokens, same declared sections. No verdict value is added or changed.
- New `_criteria_error(lines)` called from `validate` (not from `structure_error`), verifier role only. For each line under `## Criteria` that matches `^[-*]?\s*(?:\d+\.\s*)?(#\S+\s+)?(.+?): (pass|fail|unmet-dependency\s+\S+|deferred\s+\S+)\.\s*Evidence:` it records the state. It returns a reason for: a `unmet-dependency` or `deferred` line with no `#<ref>` prefix ("held criterion needs its #<ref>"); a held line that has no Evidence text; and the central rule, Verdict `pass` while any line is held or `fail` ("## Verdict pass but <ref> is <state>"). A line that does not match (the free-form lines older results use) is ignored, so every existing result still validates.
- `selftest` cases: a held line under Verdict `fail` passes; the same under Verdict `pass` fails with the reason above; `deferred` with no owner token is not matched and not held (it stays an ordinary line, which the steps.py layer reads as fail, see 5.4); an old result with only `pass` and `fail` lines validates unchanged. The existing `_steps_cases` accept-all pattern is the model for the negative control in section 7.
- `## Settles` (new, section 5.2) and `## Verified` are undeclared headings, so `structure_error` keeps ignoring them.

### 5.2 agents/verifier.md

- `## Output`, `## Criteria` line: `- #<k> <criterion>: pass | fail | unmet-dependency <subject> | deferred <owner>. Evidence: ...`. The `#<k>` ordinal is required on held lines and welcome on all.
- New rule 7, "Hold only what the handoff declares": report `unmet-dependency <subject>` only for a subject the criterion declares with `needs:` and that is still unmet (run `steps.py open --explain <dir>` or the `tickets.py` dependency test named in the brief; never infer it from a failing command alone), and `deferred <owner>` only for an owner it declares with `owner:` when the check is red or cannot run now. A criterion with no declaration that cannot pass is `fail`. A green check is `pass` whatever it declares. When one hold is wrong the verifier does not guess; it reports `fail` with the reason.
- Verdict rule: `pass` only when every criterion is `pass`. Any `fail` makes it `fail` and its note the ordinary defect note. With no `fail` and at least one held criterion, the Verdict is `fail` and `## For the next attempt` begins with `unmet-dependency: <subject>[, <subject>]` and/or `deferred: <owner>[, <owner>]` (the first line holds `unmet-dependency:` when both are present), then one line per held criterion `#<k> <state>`. When a `fail` and a held criterion both exist, the first line is the ordinary fail note; the held lines follow.
- Settling run: when the brief names criteria to re-check and says it settles them for an owner stage, the verifier checks only those, records each normally, and adds a `## Settles` section after `## For the next attempt` listing the refs that are now `pass`, one per line: ``- step-1#4``. A criterion it cannot pass stays held or becomes `fail` by the same rules.
- The existing "named list of criteria means check only those" Brief sentence is the hook; the build adds that a re-check run lists refs.

### 5.3 handoff-format

- `### Acceptance criteria` gains the bracket clause and the criterion reference, with the three-line example of section 4.
- New `## Batched verifier result` text: a task-dir verifier result may carry `## Settles` beside `## Verified`.
- New section "Held criteria": the four states, the closure rule (no ticket closes while a criterion is held), the settle path, and the pointer to `steps.py open`.
- The step-handoff note about `steps.py swap` adds that the clause is preserved.

### 5.4 steps.py

- `criteria_meta(line)`: returns `{'stage', 'owner', 'needs'}` from a trailing bracket clause or `{}`; `lint` refuses the malformed forms of section 4; `swap` refuses a new text whose clause differs from the old line's.
- `held_items(dir)`: for each criterion with a clause, finds the newest verifier result that names its `#<ref>` (a step-dir result for `step-<n>#k`, a task-dir result or a step-dir result for `ticket#k`, newest by `order.py`; a step-dir and a task-dir result are compared by their `runs.jsonl` position, both writers record `file`). State `pass` settles it. State `unmet-dependency` stays held only while the declared subject is still unmet by `tickets.py` (met: `T-NNNN` done, `file:` path exists, `cap:` provided by a done ticket); a subject that is met now makes the item `stale` (the report needs a re-check). State `deferred` stays held until a later result passes it. A held line whose criterion has no matching `needs:` subject or `owner:`, or a Verdict `pass` with any held line, is read as `fail` (fail closed): the claim is checked against the handoff, not trusted.
- `next_action`, new branches after the `inherited` and `pass` branches and before the plan-defect branch:
  - Verdict `fail` whose note starts `unmet-dependency:` and every held line verifies: if a subject is now met, `reverify L<level>` with reason "subject now met; re-check #k" (the verifier brief lists the refs); otherwise `wait`, reason "step-<n> waits on <subjects>; not a defect, no rebuild, bump or replan", with the same `read:` lines.
  - Verdict `fail` whose note starts `deferred:` and every held line verifies: `deferred`, reason "step-<n> built; <refs> owned by <owner>; the owner stage settles them".
  - Neither action is counted in the rebuild or bump count (as a plan-defect fail is not), and a verifier with held items plus an ordinary `fail` follows the ordinary path.
  - Any held line that does not verify makes the result an ordinary `fail` with reason "undeclared hold ignored: #k".
- `resume_action`: `wait` and `deferred` steps are skipped in favour of the next step whose action is not done, `wait` or `deferred`, since the held step's own build is complete. When only held steps remain it prints the first one's action, `wait` or `deferred`, with "every other step passed". A step is never printed `done` while held.
- `batch_verified` is unchanged: it counts a result only with Verdict `pass`, so a held step is never batch-verified.
- New `steps.py open <task dir>` (read-only): prints one line per held criterion, `<ref>\t<state>\t<subject or owner>`, nothing and exit 0 when none; `--explain` adds the reason a hold was read as stale or fail. Also an importable `open_items(task_dir)` for tickets.py.
- `merge_class`: the reason for a `fail` Verdict with only held items reads `held <owner or subject>` instead of `verifier fail`, so a lane waiting on its owner is not read as a defective one. The class stays `integration`.

### 5.5 tickets.py and the solo and fanout flow

- `cmd_close` calls `steps.open_items(task_dir)` before any write and refuses with `<slug>: criteria still held: <ref> <state> <who>, ...; settle them in the owner stage; nothing written`. `--force` does not bypass it (`--force` today only leaves outside refs), and `--reason` does not either (a solo ticket closes with `--reason`, and its criteria are exactly the ones that must not be dropped silently). The sanctioned exits are the owner settling the criterion, or a visible edit of the handoff (the clause removed or the criterion replaced in a replan or `swap`), which shows in the diff.
- Solo flow (`agents/solo.md`, the solo lane contract, `fanout.py` verifier prompt): a batched verifier with Verdict `fail` and only held items is not sent back to solo. The parent runs `steps.py open`, lets the lane land, and runs the owner stage's re-check (the integration verifier after the merge, which `fanout.py` already runs for lane gates) with the listed refs and "settles for <owner>"; only then does the ticket close. Solo's report says `verify: needed` as today and adds `held: <refs>`.

## 6. How an owner closes a deferred criterion

The owner stage (a gate verifier on the integration branch, a testing ticket's verifier) runs the verifier with the held refs named. A pass produces a task-dir `verifier-L<k>.md` whose Verdict is `pass` for that run, whose Criteria line for each ref is `pass`, and whose `## Settles` lists the refs. `held_items` reads it as newer than the hold and the item leaves `steps.py open`. A ticket id owner works the same way: that ticket's verifier result, copied or referenced into the holder's task dir by the conductor, is the evidence; this design does not add cross-ticket reads. A `deferred` criterion whose owner never runs keeps the ticket open, which is the intended failure mode.

## 7. Negative controls (premature closure)

All run on temp fixtures with the `_steps_cases` pattern of results.py, each with a control copy that proves the check can go red.

1. Verdict `pass` with `#4 ...: deferred integration` fails `results.py validate`. Control: a copy of results.py with the `_criteria_error` call removed validates it, so the rule is what rejects it.
2. The same fixture, validated by an accept-all results.py: `steps.py open` still lists `step-1#4 deferred integration` (fail closed at read time) and `steps.py next` prints `reverify` or the ordinary fail path, never `done`. Control: with `held_items` stubbed empty the same fixture prints `done`.
3. `tickets.py close <slug> --reason x` and `--force` on a fixture with one held criterion exit 1, write nothing, and leave the folder unrenamed. Control: the same fixture after a settling result (`## Settles` lists the ref) closes with exit 0.
4. A held line on a criterion with no `owner:` or `needs:` clause: `steps.py next` prints a counted `rebuild`, not `deferred`. Control: adding `[owner: integration]` to the handoff line changes it to `deferred`.
5. `unmet-dependency T-0307` while T-0307 is `done`: `steps.py next` prints `reverify`, not `wait`. Control: with T-0307 `ready` it prints `wait`.
6. `steps.py swap` that changes or drops the bracket clause refuses. Control: a swap that keeps it applies.
7. Old results: every existing verifier fixture in results.py `selftest`, steps.py `selftest` and check.py still passes unchanged (no held tokens, no clauses).

## 8. Migration

- Results already written have only `pass` and `fail` criterion lines, so `_criteria_error` matches nothing and `held_items` is empty: they validate, route and close exactly as before. No result file is rewritten.
- Handoffs with no bracket clause declare nothing held. A running ticket adopts the feature by adding clauses; the next verifier run may then use the new states.
- Cross-version: a runner older than the build that reads a new result sees Verdict `fail` and counts it as an ordinary fail (a rebuild) until upgraded. No result is mis-read as `pass`, so the failure is safe, only wasteful. Mixed-version lanes should run the build ticket's version everywhere before any handoff uses the clause.
- Closed tickets (`.NNNN-*`) are not scanned by `open` and never reopened.
- Release: the build targets 0.22.2; the version bump and the `check.py` model-table checks follow the repository's usual release steps in the build ticket.

## 9. Rejected alternatives

- New Verdict values (`blocked`, `deferred`, `unmet`). The ticket forbids changing the parsed values, and an unknown Verdict is "no verdict", which `next_action` reruns twice and then stops, so every held step would burn two verifier runs before stopping. It also breaks `dispatch.py` and `fanout.py` readers for old and new runners alike.
- Verdict `pass` with caveats ("pass, 2 deferred"). The Verdict is the most-read field in the pipeline (`batch_verified`, `merge_class`, fanout land, the board); one reader that checks only the first token closes the ticket prematurely. A held criterion must make the Verdict `fail`.
- A verifier free to defer any failing criterion. It turns "fails" into "deferred" with one word and no check. Requiring a handoff declaration, and re-checking the claim in `steps.py`, keeps the author of the plan, not the author of the report, in control of what can be held.
- A separate ledger file of open criteria. A second source of truth to keep in sync with the verifier results; deriving it from the newest result per criterion has no sync step.
- A waiver or `--accept-open "<reason>"` on `tickets.py close`. It is the premature-closure path itself with a reason attached. The owner settling, or a visible handoff edit, are the only exits.
- Moving the owned rows out of the lane ticket into the owner's ticket. Correct where the plan foresees it and recommended as a complement, but the evidence shows both causes arriving from outside the plan (a shared template's rows, a merge-order prerequisite), and the lane's own criteria list then no longer states what the delivered component must satisfy.
- Handling `unmet-dependency` as a replan or a `blocked` builder. The existing `stale lane:` precedent (`resplit`, never a replan) shows a missing prerequisite is not a plan defect; a replan spends a planner run and discards a sound build. `wait`, then `reverify`, spends neither.
- Ticket front matter `depends:` alone. It orders ticket starts and cannot express a prerequisite of one criterion discovered during a build, nor a criterion owned by a later stage.

## 10. Risks and open points

- Built deviations (T-0408): the ref ordinal counts bullet lines, not every line of `criteria_lines` (a blank line would shift later refs); `fanout.py land` still stops a held lane with a labelled `verifier fail (held ...)` outcome instead of letting it land before the owner settles; the live throwaway-project run of section 11 is not made.

- The criterion ordinal `#k` is positional. A hand edit that inserts a criterion line shifts later refs; `lint` should warn when a result in the step dir names a ref whose line text no longer carries its clause. The build decides whether that is a warning or a refusal.
- Comparing a step-dir result with a task-dir result by `runs.jsonl` position assumes both are recorded. A result with no record falls back to `order.py`'s name order within its own dir and loses to a recorded one.
- Cross-ticket owners (`owner: T-0310`) rely on the conductor placing the settling result in the holder's task dir. This design adds no cross-ticket read, so a ticket owner is an honest hold, not an automatic settle.
- Codex runs the verifier through `sdlc-verifier-l3` with `agents/verifier.md` as the shared contract, so the same text applies. No live Codex run was made for this design; Codex behavior is unverified.
- Verifier rule 7 asks the model to test a declared subject, and the only mechanical check is the `steps.py` re-derivation. A verifier that reports a hold on a stale subject is caught by `stale`; one that fails to hold a legitimately held criterion produces an ordinary `fail`, which is the pre-change behavior.

## 11. Build ticket outline (to file after this one closes)

Scope: `results.py` (5.1), `agents/verifier.md` (5.2), `skills/handoff-format/SKILL.md` (5.3), `steps.py` (5.4, with lint, swap, next, resume, open, merge_class), `tickets.py` close gate and `fanout.py` merge_class callers (5.5), `agents/solo.md` and the solo lane contract. Level L3 (cross-cutting; touches the verdict path). Done when the seven controls of section 7 run in `selftest` or `check.py`, `bash plugins/sdlc-lite/scripts/check.sh` passes, and a focused run in a throwaway project shows a `deferred` criterion keeping a ticket open until a settling verifier result passes it.

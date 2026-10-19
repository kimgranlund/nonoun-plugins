# Cascade guard: a per-step run cap that stops and asks, and a template-instance plan review

Status: design, proposed. Ticket T-0427 (design only, nothing built). Needs the maintainer's go before a build ticket is filed.

Paths here predate 0.23.0. Since lean work records, `<task>/runs.jsonl`, `step-<n>/` and `skips.md` writes by the runner resolve through `order.py records_dir` to the task's records dir (`.sdlc/runtime/tasks/<folder>/`); read `<task>` below as that dir for run records.

## 1. Answer in one paragraph

A shared gate counts the agent runs already recorded for the scope a dispatch is about to run in: the task's `runs.jsonl` plus, for a step handoff, that step's `runs.jsonl`. When that count is already 6, `dispatch.py prepare` (and `run.sh` on Codex) refuses with exit 6 and a fixed stop-and-ask message, so the 7th run on a step needs the maintainer's answer, given as `--cascade-override "<reason>"` and recorded in `skips.md` and on the `runs.jsonl` row. N is 6 because the two cascades the maison report names sit above it (T-0378 at 7 runs per step, T-0362 at 8) while its self-capped T-0379 sits at 6 and passes. A plan that declares itself a copy of a passed plan gets one command, run before any review, that proves its diff against that plan changes only shas, counts and ids; a plan that passes the proof gets one plan reviewer on the diff only, outside the replan cap. A plan that fails it takes the normal route. Run on the real maison pair, the proof refuses: the T-0378 plan changes 22 lines that are not shas, counts or ids, and the first T-0378 review found a real defect in one of those lines. A pass is never re-verified unless a verified file changed since, and a verifier dispatch on an unchanged build is refused by the same shared gate, which closes the T-0339 gap on both hosts. The hook that already blocks unprepared spawns in a conductor session gains one case for role sessions.

## 2. Sources

- The maison conductor's report and the maintainer's decisions of 2026-10-10: the `## Context` of the T-0427 ticket handoff, `docs/work/.0427-cascade-guard-design/handoff.md`.
- Maison evidence, read as data (never written):
  - T-0378 plan reviews `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/plan-reviewer-L1.md` (replan) and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/plan-reviewer-L1-2.md` (pass); its plans `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/planner-L3-2.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/planner-L3-3.md`.
  - T-0379 plan reviews `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0379-integration-wave-4/plan-reviewer-L1.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0379-integration-wave-4/plan-reviewer-L1-2.md` (both replan).
  - T-0362, the plan the two copied: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0362-integration-wave-2/planner-L3.md`, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0362-integration-wave-2/planner-L3-2.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0362-integration-wave-2/planner-L3-4.md`. The passed one is `planner-L3-4.md`: its `runs.jsonl` orders it after `plan-reviewer-L1.md` (replan) and before `plan-reviewer-L1-2.md` (pass).
  - T-0339 verifier cascade: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0339-examples-axe-inherited-nodes/verifier-L3.md`, the `verifier-L2.md` beside it, and that folder's `runs.jsonl`.
- Run counts: `fleet_collect.py collect` on `/Users/kimgranlund/Projects/maison/ui-kit-maison` and `/Users/kimgranlund/Projects/nonoun/agent-ui`, and a per-step tally of their `runs.jsonl` files (section 3).
- This repo: [dispatch.py](../../../plugins/sdlc-lite/scripts/dispatch.py) (`prepare` line 622, budget gate lines 720 to 724, lock line 726, `--routing-reason` line 1215), [run.sh](../../../plugins/sdlc-lite/scripts/run.sh) (lane gate lines 340 to 357, budget gate lines 373 to 380, exit codes line 66), [steps.py](../../../plugins/sdlc-lite/scripts/steps.py) (`review_required` line 2586, `review_action`, the cap `if len(replans) >= 2:` line 2684), [fleet_collect.py](../../../plugins/sdlc-lite/scripts/fleet_collect.py) (`runs.by_ticket`), [block-role-spawn.sh](../../../plugins/sdlc-lite/hooks/block-role-spawn.sh), [hooks.json](../../../plugins/sdlc-lite/adapters/claude/hooks.json) line 19, [hook-selftest.sh](../../../plugins/sdlc-lite/scripts/hook-selftest.sh) from line 25, [verifier.md](../../../plugins/sdlc-lite/agents/verifier.md) line 33, [plan-reviewer.md](../../../plugins/sdlc-lite/agents/plan-reviewer.md) line 17, [planner.md](../../../plugins/sdlc-lite/agents/planner.md) line 18, [conductor.md](../../../plugins/sdlc-lite/agents/conductor.md) line 9, [bounded plan correction](bounded-plan-correction.md) (T-0421), [verifier held criteria](verifier-held-criteria.md) (T-0400), [K-004](../../kpi/004-unsatisfiable-criteria-caught.md).

## 3. Cascade counter

### What is counted

The count is agent runs per ticket step, read from `runs.jsonl` records, never from file times or result names:

- A step handoff (`<task>/step-<n>/handoff.md`): the non-empty lines of `<task>/runs.jsonl` plus those of `<task>/step-<n>/runs.jsonl` and of any `<task>/step-<n>.superseded-<k>/runs.jsonl`. The plan stage is shared by every step, so a planning cascade weighs on each step built from it; a resplit loop on one step is a cascade too.
- A task handoff (planner, plan-reviewer, architect, filer): the lines of `<task>/runs.jsonl` only.
- A row counts whatever its exit code: a failed run was still a run. A row that records no model run does not count: a T-0421 `route correction` row and the template proof row of section 4 (`route template-check`).

### Where it is checked

In `prepare` (`def prepare(role, level, handoff, ...)`, dispatch.py line 622), directly after the budget gate and before the lock, so a refusal writes no attempt record, dispatch record or `runs.jsonl` line:

```python
    if 'budget' not in skip:
        ticket = budget.ticket_of(handoff)
        rep = budget.report(ticket) if ticket is not None else None
        if rep and rep['state'] != 'ok':
            raise Refuse(4, 'dispatch.py: budget %s%%: ask the user; budget.py ack' % rep['percent'])
    # <- the cascade gate goes here: cascade.check(handoff), Refuse(6, ...) unless cascade_override

    lock = None
```

The count itself lives in a new shared script, `cascade.py`, because `prepare` is the Claude path only (it refuses unless `SDLC_BACKEND` is `claude`). `run.sh` calls the same script after its budget gate (line 373), exactly as both already call `budget.py`. One count, two callers, both hosts.

### The rule and the message

Refuse when the count before this dispatch is 6 or more. N = 6: at most 6 runs per step scope without asking; the 7th asks. Exit code 6 (free in both scripts: `prepare` uses 2, 4 and 5; `run.sh` uses 0 to 5). `prepare` prints, verbatim, on stderr:

```text
dispatch.py: cascade cap: <task dir>[/step-<n>] already has <k> agent runs (<t> task, <s> step; cap 6). Stop and ask the maintainer before running <role> <level> again; do not continue on your own.
dispatch.py: if the maintainer says run it, prepare again with --cascade-override "<the maintainer's reason>"; it is recorded in skips.md and runs.jsonl.
```

`run.sh` prints the same two lines with the prefix `run.sh:` and `SDLC_CASCADE_OVERRIDE="<the maintainer's reason>"` in place of the flag. The conductor's answer to exit 6 is one `AskUserQuestion`, never a retry; a headless lane (`SDLC_HEADLESS=1`) stops with the message as its blocked reason.

### The override

- Claude: `dispatch.py prepare <role> <level> <handoff> --cascade-override "<reason>"`. A flag and not an environment variable, for the reason `--routing-reason` gives at line 1215 (a command that starts with `VAR=...` misses a `Bash(python3:*)` allowlist). Codex: `SDLC_CASCADE_OVERRIDE="<reason>"` on `run.sh`, like `SDLC_LANE_OVERRIDE`.
- An empty or whitespace reason is refused as usage (exit 2).
- Recorded twice: one line `cascade override: <role> <level> run <k+1> over cap 6: <reason>` appended to the task dir's `skips.md` (the file `lane_override` already writes), and a `cascade_override` field on the dispatch JSON and on the `runs.jsonl` row `record` writes, beside `lane_override`.
- An override covers that one dispatch. The next run on the same scope asks again. There is no ack file that lifts the cap for the rest of the ticket (section 10).

### Why 6

Counts rerun on 2026-10-11 for this design:

- Collector, per ticket folder (deduplicated): `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --du-timeout 20` gives 1895 runs over 339 ticket folders, median 2 runs per ticket, 90th percentile 11; T-0378 10 (builder 4, plan-reviewer 2, planner 2, verifier 2), T-0362 10, T-0379 8, T-0339 3 (solo 1, verifier 2). The same command on `/Users/kimgranlund/Projects/nonoun/agent-ui` gives 218 runs over 40 folders, median 3, 90th percentile 10. These match the plan-time numbers (1894 then; one run landed since).
- Per step scope, the quantity the gate counts: task rows plus step rows for each `step-<n>` dir, task rows alone for a task with no step dirs, over every `runs.jsonl` that `find <repo>/.sdlc -name runs.jsonl` lists (dot folders included; `tool-runtimes` and `bench` trees left out). A read-only Python tally gives:
  - maison: 822 task dirs, 1131 step scopes, median 2, 90th percentile 9, 95th 11, max 13. T-0378 steps 1 and 2: 7 each (4 task + 3 step). T-0362 step 1: 8, step 2: 7. T-0379 steps 1 and 2: 6 each.
  - agent-ui: 40 task dirs, 64 step scopes, median 6, 90th percentile 16, max 18 (`no-barrels`, whose task `runs.jsonl` alone holds 14 rows: 6 planner and 5 plan-reviewer runs).
  - Step rows alone are small: maison step dirs median 2, 90th percentile 3, max 8; agent-ui median 2, max 4. The cascades are in the plan stage plus the step together, which is why the gate counts both.
- Share stopped once or more, by N (a scope over N means its run N+1 asked):

| N | maison scopes over N | maison tasks that ask | agent-ui scopes over N | agent-ui tasks that ask |
|---|---|---|---|---|
| 5 | 262 (23.2%) | 78 (9.5%) | 34 (53.1%) | 10 (25.0%) |
| 6 | 241 (21.3%) | 67 (8.2%) | 27 (42.2%) | 6 (15.0%) |
| 7 | 185 (16.4%) | 39 (4.7%) | 19 (29.7%) | 6 (15.0%) |
| 8 | 163 (14.4%) | 32 (3.9%) | 14 (21.9%) | 2 (5.0%) |
| 10 | 61 (5.4%) | 21 (2.6%) | 9 (14.1%) | 1 (2.5%) |
| 11 | 5 (0.4%) | 3 (0.4%) | 9 (14.1%) | 1 (2.5%) |

- N rests on the per-step tally, not on the collector's per-ticket total, because the gate counts per step. N = 6 is the largest value that still stops both named cascades (T-0378 at its 7th run on each step, T-0362 at its 7th on step 1) and lets the self-capped T-0379 (6) through. It asks on 8.2% of maison tasks and 15% of agent-ui tasks, once each; an ask is one question, while the second plan review and the replan on T-0378 cost about 40 to 60 minutes (the maison report). N = 7 or 8 would miss T-0378, the case the report is about.
- The two T-0378 numbers come from different tallies and both stand. The collector deduplicates and counts the ticket folder as a whole: 10. Maison's conductor counted 11 agent runs on steps 1 and 2 itself, and the ticket folder holds no `planner-L3.md` beside `planner-L3-2.md` and `planner-L3-3.md`, which fits a first planner run that left no row. The gate counts rows, so it sees 7 per step.
- The 6 is the same number `conductor.md` line 9 already uses ("at the cascade cap (6 until T-0427 sets it)"). That wording is T-0428's; the counter ticket only drops the "until" clause.

## 4. Template-instance plan review

### The proof is one command

The planner names the passed plan in a line `Template: <path of the passed plan> sha256=<digest>` (planner.md line 18 already says a copy names its plan). The proof normalizes every sha (7 to 40 hex digits holding at least one digit) to `<sha>` and then every digit run to `<n>`, so ticket ids, counts and step numbers all compare equal, and diffs the normalized lines. A line that differs only in those tokens is mechanical; anything else is printed with its line number, and the command exits 1:

```sh
python3 - <passed plan> <new plan> <<'EOF'
import sys, re, difflib
def norm(s):
    s = re.sub(r'\b(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}\b', '<sha>', s)
    return re.sub(r'[0-9]+', '<n>', s)
a, b = (open(p, encoding='utf-8').read().splitlines() for p in sys.argv[1:3])
na, nb = [norm(x) for x in a], [norm(x) for x in b]
mech = other = 0
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, na, nb, autojunk=False).get_opcodes():
    if op == 'equal':
        mech += sum(a[i] != b[j] for i, j in zip(range(i1, i2), range(j1, j2)))
        continue
    other += max(i2 - i1, j2 - j1)
    for i in range(i1, i2): print('- %d: %s' % (i + 1, a[i][:160]))
    for j in range(j1, j2): print('+ %d: %s' % (j + 1, b[j][:160]))
print('template-diff: %d lines differ by sha, count or id only; %d other lines' % (mech, other))
sys.exit(1 if other else 0)
EOF
```

The build moves this into `steps.py template <task dir> --check <passed plan> <new plan>` with the same output, and adds the `Template:` digest check.

### What it printed on the maison pair

- T-0362 `planner-L3-4.md` (passed) against T-0378 `planner-L3-2.md` (the copy the first review saw): exit 1, `template-diff: 44 lines differ by sha, count or id only; 22 other lines`. The 22 lines are not shas, counts or ids:
  - counts written as words and a changed noun: line 3 `Land the six remaining verified lanes` became `Land the ten verified branches`; the step 1 title and line 19 the same;
  - the merge list grew from six entries to ten, with new branch names: old lines 29 to 33 (`T-0362: merge t0353-s1` ... `codex/0348-shared-refs`) against new lines 29 to 37 (`T-0378: merge codex/0371-project-handoff` ... `codex/0353-page`), and line 27 gained a sentence on how Card and OptionCard arrive;
  - changed reasoning: line 35 (merge bases), line 37 against 41 (the conflict expectation);
  - changed checks: line 39 against 43 (the authored-only test list), line 57 against 61, criteria lines 73, 74, 77 and 83 against 77, 78, 81 and 87, where the `t0362-int` worktree path and the test commands changed;
  - line 157 against 161 (which tickets close).
- T-0362 `planner-L3-4.md` against T-0378 `planner-L3-3.md` (the replan that passed): exit 1, `template-diff: 41 lines differ by sha, count or id only; 40 other lines`.
- Controls: the T-0362 plan against itself prints `0 ... 0 other lines`, exit 0. A copy with one sha swapped and `six` changed to `seven` prints `3 lines differ by sha, count or id only; 1 other lines`, exit 1: a count written as a word is not a count to the check, so it fails closed.

So the maison claim that T-0378 was the T-0362 plan "with shas and counts swapped" does not hold under the proof. The route would have refused it and sent it the normal route, and rightly: the first T-0378 review's step 2 finding was a real defect in exactly such a line (the criterion wanted `git rev-list --merges --count main..HEAD` to equal 10, while one lane carried its own merge commit, so a correct build counts 11). The other findings of that review were stale T-0362 premises copied unchanged into Assumptions, and the reviewer noted the Do was unaffected. A diff-only review would not see those; the cost of missing them is a stale Assumptions line, not a wrong build, because the step verifier still runs every criterion.

### The route

- `steps.py review` prints a new action `template-review L1` when the newest plan has a `Template:` line, the named plan's digest matches, that plan has a plan review with Verdict `pass` that counts after it (or no review was required for it), and the proof exits 0. Before printing it, `steps.py` appends a `runs.jsonl` row `route template-check` (no model, not counted by section 3) with both digests and the mechanical line count.
- One plan reviewer, at L1, gets the diff only: the proof's output and the changed line pairs, not the whole plan. It answers whether each changed sha, count or id is right for this ticket, and returns `pass` or `replan` in the normal format. Its result carries a `Review: template` line, and its `runs.jsonl` row carries `route template`.
- That review does not count against the replan cap. `review_action` leaves `route template` reviews out of `replans`, the way T-0421 leaves out a consumed `token-fix` review. A template review that says `replan` sends the plan the normal route with the whole cap still available.
- One template review per task dir. A second template plan in the same task dir takes the normal route.

### What forces the normal route

- The proof prints any other line (exit 1), including a count written as a word, a new or removed line, a renamed branch, a changed command or a changed Assumptions line.
- No `Template:` line, a digest that does not match the named plan (the passed plan changed since it passed), or a named plan with no counting `pass` review when one was required for it.
- An unresolved assumption in the new plan (`review_action` stops first, as today).
- A template review that says `replan` or `blocked`.
- A second template plan in the same task dir.

The step level (L4 or L5) does not force the normal route: the template review is the review `review_required` asks for.

### The skip rule: a pass is not re-verified

The maintainer's rule: a reviewed pass is never re-verified unless a verified file changed since. Mechanically:

- A plan with a counting `pass` review: `prepare` refuses another `plan-reviewer` dispatch on that task dir while the newest plan's digest equals the digest the pass reviewed (exit 2, `plan <name> already passed review <name>; a new review needs a changed plan`).
- A verifier `pass`: `record` adds `verified_diff_sha256` to the verifier's `runs.jsonl` row, the SHA-256 of `git diff <base-sha> -- . ':(exclude).sdlc'` in the execution tree. `prepare` for a verifier on that dir recomputes it; while it is equal and the handoff digest is the one the pass verified, the dispatch is refused (exit 2, `<dir> already passed verification <name>; nothing it verified changed since`). The cascade override does not lift this refusal; a changed file or a changed handoff does.

## 5. Verifier never spawns a verifier

### What is enforced today

`block-role-spawn.sh` is a `PreToolUse` hook registered under the `Agent` matcher in `plugins/sdlc-lite/adapters/claude/hooks.json` line 19. In a conductor session (agent type `sdlc-lite:conductor` or `conductor`, or `SDLC_ROLE=conductor`) it:

- allows an `sdlc-lite:<role>-L<n>` spawn only as a prepared dispatch: the name is `<ticket>-<role>-L<n>[-<k>]`, a dispatch record beside the prompt's `Handoff:` names that agent, and the call's model equals the record's model (so a verifier cannot be moved onto the builder's family);
- denies a fork named `verifier-` or `plan-reviewer-`, and any fork without a `Fork reason:` line;
- denies another plugin's agent whose name holds a builder, verifier, reviewer, planner or checker token;
- lets the messenger through under its `inbox-<repo>-<receiver>` name.

Every other session exits 0 at the agent-type check, so a verifier sub-agent's own `Agent` call is not gated at all. [hook-selftest.sh](../../../plugins/sdlc-lite/scripts/hook-selftest.sh), from line 25, has a deny case for each of the four conditions and the allow cases. The rule against a second verifier is prose today: verifier.md line 33 ("a pass is final. Never spawn or request another verifier on your own report") and conductor.md line 9.

### What holds on Codex

Claude hook enforcement does not imply Codex enforcement. No Claude hook runs on Codex: a Codex role runs through `run.sh` or the native subagent exchange, and nothing mechanical stops a Codex verifier, or a Codex conductor, from dispatching a second verifier on an unchanged build. What holds on both hosts is what lives in the shared scripts both paths call: the skip rule of section 4 and the counter of section 3, through `cascade.py` called from `prepare` and from `run.sh`.

### The gap T-0339 shows

The maison T-0339 `verifier-L3.md` returned `fail` with a `plan defect:` line: the Done-when (zero serious axe nodes on every sitemap page) contradicted the Non-goals (other pages). The conductor restated the criterion and dispatched `verifier-L2` with the routing reason `re-verify the restated criterion only, using verifier-L3 evidence`. That verifier re-ran every criterion on the same build (the same commits `8989cf1a5..d396cf8e8`), including a 12.6 minute Playwright run of 1039 tests the first verifier had already passed. Both dispatches were prepared, so the hook allowed both. Nothing tied the second verifier to a changed build, and nothing held it to the one changed criterion.

### The rule that closes it

- Shared gate (both hosts): a verifier dispatch on a dir whose newest verifier result counts after the newest build, with `verified_diff_sha256` unchanged, is refused unless the handoff's criteria changed since that verdict. When they changed, the dispatch must be a re-check run that names only the changed criteria (the verifier's existing named-list brief, verifier.md line 11), and the criteria the earlier verdict passed carry forward. A `plan defect:` verdict routes to a replan or to the maintainer, never straight to a second verifier.
- Hook (Claude): `block-role-spawn.sh` gains one case before its agent-type check. When the session's role (from `_role.sh`) is `verifier` or `plan-reviewer`, a spawn of `sdlc-lite:verifier-*` or `sdlc-lite:plan-reviewer-*`, or a fork, is denied with `<role> session: a verifier never spawns a verifier; report plan defect and let the conductor route it`.

## 6. Relation to T-0421 and the replan cap

- The replan cap: `review_action` in `steps.py` stops and asks once two plan reviews in the task dir say `replan` (`if len(replans) >= 2:`, line 2684), and the planner has one replan of its own. A replan is reviewed only when `review_required` (line 2586) finds a step at builder L4 or L5.
- [T-0421](bounded-plan-correction.md) adds a sibling route: a script-proven two-line correction of a reviewed plan, whose consumed `token-fix` review is counted out of the cap, one per task dir. The template route has the same shape on a different input: a new plan proven against another ticket's passed plan. Both are proven by a command before any model runs, both are one per task dir, both leave their review out of `replans`, and both fall back to the normal route with the cap intact. Neither raises the cap.
- The counter and T-0421: the `route correction` row and the `route template-check` row record no model run, so they do not count. The template review itself is a model run and counts as one run; it does not count as a replan.
- The counter and the cap together: the normal one-step path is planner, plan review, builder, verifier, 4 runs. One replan with its review makes 6, and then a failed build's rebuild is the 7th run and asks. The longest plan stage the cap allows (template review saying replan, then planner, review, planner, review) is 6 task rows, so the first builder asks. That is deliberate: by then the plan stage alone has cost a full step.
- [T-0400](verifier-held-criteria.md): a held criterion (`unmet-dependency` or `deferred`) waits or holds instead of a rebuild. A settling run is a verifier run on named refs; it counts as a run, and the skip rule does not refuse it because its criteria are held, not passed.
- Out of this design: T-0428 owns the wording (the doctrine lines in conductor.md line 9, verifier.md line 33, plan-reviewer.md line 17 and planner.md line 18), closed in `docs/work/.0428-close-first-doctrine/`. T-0429 owns the docs-only verifier skip, built as [verify_scope.py](../../../plugins/sdlc-lite/scripts/verify_scope.py), closed in `docs/work/.0429-skip-verifier-docs-only/`. Neither is changed here.

## 7. Measures

Three measures in the K-004 shape, each computed from `runs.by_ticket` (`{ticket folder: {role: count}}`), so each is per ticket, not per step. A per-step measure needs a collector change (build ticket 4). Before values from the 2026-10-11 collector runs above.

One measure command prints all three for a repo:

```sh
python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --du-timeout 20 | python3 -c "import json,sys;bt=json.load(sys.stdin)['runs']['by_ticket'];n=len(bt);t=sorted(sum(r.values()) for r in bt.values());pr=sum(r.get('plan-reviewer',0)>=2 for r in bt.values());vb=sum(r.get('verifier',0)>r.get('builder',0)+r.get('solo',0) for r in bt.values());print('tickets %d runs %d median %d p90 %d; plan-review>=2 %.1f%%; verify>build %.1f%%'%(n,sum(t),t[n//2],t[int(.9*n)],100*pr/n,100*vb/n))"
```

It printed `tickets 339 runs 1895 median 2 p90 11; plan-review>=2 7.7%; verify>build 12.7%` for maison and `tickets 40 runs 218 median 3 p90 10; plan-review>=2 17.5%; verify>build 2.5%` for agent-ui.

**Repeated plan review.**
- Unit: percent of ticket folders with two or more plan-reviewer runs.
- Direction: down. Target: `<= 5` in each repo.
- Baseline: maison 7.7 (26 of 339, T-0362, T-0378 and T-0379 among them); agent-ui 17.5 (7 of 40).
- Measure: the command above, `plan-review>=2`.
- Read: per retro window (`--since <date>`). The template route and the cap both push it down; a rise means plans keep failing review, not that the guard is wrong.

**Verification without a build.**
- Unit: percent of ticket folders whose verifier runs outnumber their builder plus solo runs.
- Direction: down. Target: `<= 3` in each repo.
- Baseline: maison 12.7 (43 of 339, T-0339 among them); agent-ui 2.5 (1 of 40).
- Measure: the command above, `verify>build`.
- Read: a verifier run with no build behind it is a re-verify. The skip rule and the shared verifier gate should take maison toward agent-ui's level. It undercounts a re-verify after a rebuild.

**Agent runs per ticket, 90th percentile.**
- Unit: runs.
- Direction: down. Target: `<= 8` in each repo.
- Baseline: maison 11 (median 2); agent-ui 10 (median 3).
- Measure: the command above, `p90`.
- Read: the tail the counter cuts. A low median with a high tail is the cascade signature; the median should not move. When the collector gains `runs.by_step` (build ticket 4), the share of step scopes over the cap replaces this as the direct measure (baseline from section 3: maison 21.3%, agent-ui 42.2%).

## 8. Files a build changes

- `plugins/sdlc-lite/scripts/cascade.py` (new): the count of section 3, `check <handoff>` with exit 6 and the message, `--selftest`.
- `plugins/sdlc-lite/scripts/dispatch.py`: the gate after the budget gate, `--cascade-override`, the `skips.md` line, the `cascade_override` dispatch field and `runs.jsonl` field, `verified_diff_sha256` on a verifier pass row, the plan-review and verifier skip refusals, the header's gate list and exit codes, selftest cases.
- `plugins/sdlc-lite/scripts/run.sh`: the same gate through `cascade.py` after the budget gate, `SDLC_CASCADE_OVERRIDE`, exit 6, the `runs.jsonl` field, the verifier skip refusal, the header.
- `plugins/sdlc-lite/scripts/steps.py`: the `template` verb (`--check`), the `template-review` action in `review_action` and `next_action`, the `route template` exclusion from `replans`, the usage text, selftest cases.
- `plugins/sdlc-lite/scripts/results.py`: the planner `Template:` line and the plan-reviewer `Review: template` line.
- `plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/agents/plan-reviewer.md`: the `Template:` line, and the diff-only template review brief.
- `plugins/sdlc-lite/agents/conductor.md`: line 9 drops "until T-0427 sets it"; exit 6 is one `AskUserQuestion`.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: the `template-review` action and the exit 6 stop.
- `plugins/sdlc-lite/hooks/block-role-spawn.sh` and `plugins/sdlc-lite/scripts/hook-selftest.sh`: the role-session case and its allow and deny cases.
- `plugins/sdlc-lite/scripts/fleet_collect.py`: `runs.by_step` and a `cascade_overrides` count.
- `docs/kpi/` three new measure files for section 7, and `docs/references/claude-hooks.md` for the hook case.
- `plugins/sdlc-lite/scripts/check.py`: run the `cascade.py` selftest.
- Generated Codex agent files are regenerated with `plugins/sdlc-lite/scripts/codex_roles.py`, not edited.
- `docs/specs/sdlc-lite/cascade-guard.md` and `docs/specs/sdlc-lite/README.md`: status from proposed to built.

## 9. Build tickets

1. Cascade counter, L3. `cascade.py`, the gates in `dispatch.py prepare` and `run.sh`, the override and its records, conductor and chain lines, the `check.py` selftest hook. Negative control: a task dir with 4 task rows and 2 rows in `step-1`; `prepare builder L2 step-1/handoff.md` exits 6 with the message verbatim and writes no attempt, dispatch or `runs.jsonl` line; `--cascade-override "selftest"` exits 0 and writes the `skips.md` line and the field; adding a `route correction` row to a scope of 5 does not trip the gate. A copy of `prepare` with the gate removed must make the first case exit 0, which shows the gate is what refuses.
2. Verifier skip and the second-verifier rule, L3. `verified_diff_sha256`, the verifier and plan-review skip refusals in both scripts, the `block-role-spawn.sh` role-session case. Negative control: a step with a verifier `pass` and an unchanged tree; `prepare verifier` is refused naming the passed result; touching one file in the step's diff lets it through; a hook payload with agent type `sdlc-lite:verifier-L3` spawning `sdlc-lite:verifier-L2` exits 2 with the message, and the same spawn from a conductor session with a valid record exits 0.
3. Template-instance plan review, L3. `steps.py template`, the `template-review` action, the cap exclusion, `results.py`, planner and plan-reviewer briefs, the chain action. Negative control: a synthetic pair built like the maison one (a merge list that grows by one line) is refused with that line printed and goes the normal route; a sha-only and count-only pair gets `template-review L1`; a template review that says `replan` followed by one normal `replan` review leaves `review` at `replan`, not `stop`; editing the passed plan after its pass (digest mismatch) forces the normal route.
4. Measures and per-step collection, L2. `fleet_collect.py` `runs.by_step` and `cascade_overrides`, the three `docs/kpi/` files. Negative control: a fixture with one ticket holding two plan-reviewer rows and one holding one; the measure counts only the first; a selftest that reads `by_role` instead of `by_ticket` must fail.

Tickets 1 and 2 touch `dispatch.py` and `run.sh`, so they run in sequence, not in parallel lanes. Tickets 3 and 4 touch neither and can run beside them.

## 10. Rejected alternatives

- Count per ticket, from `runs.by_ticket`: a clean nine-step ticket legitimately reaches 20 or more runs, so a per-ticket cap either asks on every large ticket or sits too high to stop a one-step cascade. The ticket total stays the measure, not the gate.
- Count step rows only: the named cascades are mostly in the plan stage (T-0378 and T-0379 each have 4 task rows: two planner runs and two plan reviews). Step rows alone have a maison 90th percentile of 3 and a max of 8, and would not see them.
- N = 8, the longest path the existing caps allow without a loop: it misses T-0378 (7 per step), the case the report is about.
- N at the 95th or 99th percentile (11): asks on 0.4% of maison tasks but never on a named case.
- A dollar cap through `budget.py`: Claude sub-agent costs are often unmetered, and a cap on a missing price is no cap. A run count needs no price, and the budget gate stays as it is beside it.
- An ack file that lifts the cap for the rest of the ticket, like `budget-ack.md`: one ack would silence every later run on the ticket, which is how a cascade continues. A per-dispatch override keeps each run past the cap a decision.
- Doctrine only (the T-0428 wording): the maintainer chose doctrine plus hard caps, and a prose rule is not checked anywhere a script could refuse.
- Trust the planner's own claim that a plan is a copy: T-0378 was presented as a copy, the proof finds 22 other lines, and the first review found a real defect in one of them.
- Widen the proof to accept number words, renamed branches or a longer merge list: those are the lines where the T-0378 defect was. A proof that accepts them proves nothing about the copy.
- Enforce "a verifier never spawns a verifier" in the hook only: a Claude hook does nothing on Codex, and the T-0339 second verifier was a prepared conductor dispatch the hook rightly allowed. The shared gate is the rule; the hook case is a second line on Claude.
- Let the template review count toward the replan cap: a review of a proven copy is not the signal the cap exists for (a plan that keeps failing review), and counting it would bring the stop one review sooner on a plan that was never rejected.

## 11. Open questions

- The per-step tally counts every row of a task's `runs.jsonl`, including scout, architect and filer rows. Should the counter leave out roles that ran before planning? At N = 6 it changes little in the data above, but a ticket with a scout, a researcher and an architect starts its first step at 3.
- `verified_diff_sha256` assumes the verifier never changes the tree it verified. The maison T-0339 verifier left two generated files modified by its own test run. The build should say whether such a change counts as "a verified file changed since".

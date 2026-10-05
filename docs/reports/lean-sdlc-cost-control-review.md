# Lean SDLC cost control review

Recorded: 2026-10-04. Independent review of `docs/lean-sdlc/cost-control.md` v0.1 (branch `cost-control`, commit 8b6b3f9 after merging main). The reviewer was the `architect` role, `run.sh architect L1` (Fable, effort high), a different family from the author (Sonnet). Result file: `.sdlc/lean-sdlc-cost-review/architect-L1.md` on the `cost-control` branch.

## Verdict

Ready after fixes. The problem statement and the "what already exists" list were supported to the dollar and by path and line. Three blockers and fifteen other findings applied to the filing plan; v0.2 applies all eighteen. v0.2 was not re-reviewed.

## Findings and what v0.2 did

| # | Severity | Finding | v0.2 |
| --- | --- | --- | --- |
| 1 | blocker | `red` at a base checkout cannot see earlier uncommitted steps, so the T-0183 step 3 class passes the gate; the replay claim is unmeetable | `red` runs in the current tree under the existing guard snapshot; `red --base` is pre-build only; a duplicate-span finding added to `check` |
| 2 | blocker | A edits `planner.md` but does not wait for T-0202 | A2 waits for T-0202 (and T-0201, T-0197); A1's one-line edit waits for T-0202 if it touches the same section |
| 3 | blocker | B and D edit `conductor.md`, owned by T-0199 | B and D edit no conductor text; both depend on T-0199 and the stop rule is its (d) |
| 4 | major | `SDLC_TMP_WORKTREES` exists only in a role run | `<toplevel>/.worktrees/tmp/specgate-<pid>` |
| 5 | major | A second criterion parser would drift | `specgate.py` imports `steps` |
| 6 | major | The `run.sh` refusal must sit before `exec run_lifecycle.py`; exit code unstated | Before the exec, exit 2; `SDLC_SPECGATE=off` recorded on the run line |
| 7 | major | `run.sh`, not `run_lifecycle.py`, writes the run line | Lifecycle records the hash and env; `run.sh` rehashes and writes the fields |
| 8 | major | A stale planner rerun is `planner-L3-2.md` and reads as a replan; `rerun` is a new action class | Stale results excluded in `review_action`, `lean_warnings`, `footprint`, one shared helper; `rerun` is a distinct action |
| 9 | minor | No `hooks/hooks.json`; registration is `adapters/claude/hooks.json`; `MultiEdit` unused; Edit payload unprobed | Corrected path and matcher, live probe added |
| 10 | major | `replan-handoff` as a second file is invisible to `read_goal` | Scripted form of the chain append into `handoff.md`, refuses without a `replan` verdict |
| 11 | major | Exit 3 is taken | Budget stop is exit 4 |
| 12 | major | D at L2 changes a parsed contract | D is L3 |
| 13 | minor | A step dir carries no front matter | `ticket_of` walk-up bounded by the `.sdlc` root |
| 14 | minor | Codex runs record no cost; the board sum is one level deep | Stated as a limit; board reads `budget.py status` |
| 15 | minor | The board table is pinned byte for byte | Budget column gated like ID and Ticket |
| 16 | minor | `(red)` is opt-in and swap parity covers `(guard)` only | Named as a limit; A2 extends swap parity |
| 17 | minor | Numbers: 78 runs, $190.43; T-0202 is $25.26, median about $24; replan windows mixed | Table, per-ticket costs, median and window notes corrected |
| 18 | minor | Verifier L3 is the second cost line and untouched | Named as a lever, with the model choice left to the user |

The review also rejected the addendum's `slow-commands.json` and `measure` (replaced by a plan-level `guard timeout:` line) and split A into A1 and A2 so the free gate ships first.

## Limits

- Read against plugins identical to main at 6658615 plus 355e853 docs; line numbers drift with T-0196, T-0197, T-0199, T-0200 and T-0201, so each ticket's plan must re-read them.
- The recount was pinned at 17:34 UTC while other sessions kept appending `runs.jsonl`.
- The Edit tool payload shape (`tool_input.file_path`) is unverified in this repository.

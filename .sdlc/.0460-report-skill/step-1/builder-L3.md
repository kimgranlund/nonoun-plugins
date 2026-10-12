<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/scripts/report.py: new file, mode 755 to match most sibling scripts. It has the `collect`, `render` and `selftest` subcommands. Stage 1 reads records and stage 2 reads the transcript. `VERBS`, `CollectorError`, the views, the options, the snapshot and `--compare last` follow the handoff names.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/docs/specs/doc-standards/core.md: new `## Status verbs` section after `## Status words`. It has the 11 verbs on one comma-separated line and the tense rule.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/docs/references/glossary.md: new `| status verb | noun | ... |` row between `step` and `ticket`. It has the verb list and the tense rule.

## Checks
- `redck.py record .sdlc/0460-report-skill/step-1/handoff.md`, run before the first edit: exit 0, 8 pre-edit controls recorded red.
- `docs_check.py --root .`, right after the two doc edits: exit 0, `0 errors, 26 warnings`. All the warnings are in files this step did not touch.
- `report.py selftest`, first run: exit 1. Three controls were green even with the rule in place:
  - `stalled`: untracked dirs hid file mtimes. Fixed by using `git status --porcelain --untracked-files=all`.
  - `trivial last failure`: the fixture had no running attempt, so it had no task. Fixed by giving the fixture a running attempt.
  - `check first run late`: the criteria live under `### Acceptance criteria`, which `section()` did not read. Fixed by letting `section()` take a heading level.
- `report.py selftest`, second run: exit 0. All 25 controls print `ok: control <name>: red without the rule, green with it`, including the 12 required ones. The 8 other cases also pass.
- Criterion 1 (the selftest has the 12 named controls): rc 0.
- Criterion 2 (`render nosuchview` exits 2 and stderr lists every view plus `--no-snapshot` and `--compare`): rc 0.
- Criterion 3 (summary has 1 to 8 lines): rc 0. The live summary is 6 lines.
- Criterion 4 (`render full` prints all 8 `<view>:` headers): rc 0.
- Criterion 5 (JSON has the schema, the nine groups and the `health.context` check): rc 0.
- Criterion 6 (`report.VERBS` has 11 verbs and all appear in core.md): rc 0.
- Criterion 7 (the exact verb line is in core.md): rc 0.
- Criterion 8 (glossary has `| status verb |`): rc 0.
- Criterion 9 (`docs_check.py --root .`): the in-sequence run printed `0 errors` but the exit code capture was blank under zsh (`PIPESTATUS`). A standalone re-run gave `docs_rc=0`.
- Criterion 10 (scope check against `SDLC_BASE_SHA=ebac4973`): rc 0.
- Extra live probes:
  - `render tasks signals --only timeline,health --format md --since 2d --last 2 --no-snapshot`: rc 0.
  - `render --session x`: refused with the list of views.
  - `render` without `CLAUDE_PID` and `CLAUDE_CODE_SESSION_ID`: rc 0, state `idle`, 32 fields in `unknown`.
  - `git diff --check`: clean.

## Notes
- Interpretation choices where the handoff left room:
  - **Exit 2 for an unreadable record** covers only records the user points at: a non-numeric `report.*` line in `.sdlc/config`, and the `--compare last` snapshot. A malformed `*.attempt.json` or `runs.jsonl` found while scanning goes to `unknown`, so a stray file never breaks a live render. A bad `runs.jsonl` gives `cost.dollars` in `unknown`, never 0.
  - **State `stalled`** is added because the handoff asks for it; the schema draft's state list does not include it. A thread with a running child or an open question is not counted as stalled.
  - **Fixed thresholds:** `check first run late` (position 0.9), `dead-end work` (more than 0) and `dead` have no `report.*` key in the draft, so their thresholds are fixed in the code. `--explain` prints them.
  - **`recent`** takes closed tickets from the whole repo inside the window, timed by the newest `finished_at` in their attempt files (else the last `runs.jsonl` `ts`). Builder and verifier results come from the thread's task only, or from all open tasks when no task is known.
  - **Summary lines:** besides state, needs, now, next and grade, the summary adds `recent:` and `unknown: N fields` when they are not empty. It still prints at most 8 lines.
  - **`now`** calls `steps.py next` only when no attempt is running. Otherwise the entry comes from the running attempt file.
  - **Intended next items:** they come from the bullets under a task handoff's `## Next` section. A bullet that names no ticket and no step is marked `intended`; computed items (later steps, dependent tickets, the ready queue) are `planned`.
  - **`waiting-on-user`** is guessed partly from text: it fires on an `AskUserQuestion` with no result, or when the last assistant text ends in `?`.
  - **Selftest stubs:** the selftest replaces `gate_lock.py status`, `budget.py status` and `steps.py next` with stubs, so it never reads the machine-wide gate-lock state that causes the T-0459 flake. The live render ran the real calls: the gate queue was empty, budget `no budget`, next action `build L3`.
- Live render on this repo, for comparison:
  - state `waiting-on-role`, grade A with no flags
  - now: `building step 1 T-0460`; next: step 2, then T-0461 (both `planned`)
  - cost `$1.84 (1 priced, 0 unpriced)`, peak context fill 37%
  - 5 fields in `unknown`: `health.unpushed_commits`, `identity.level`, `identity.name`, `identity.parent`, `outcome.last_result`
- Every probe used `--no-snapshot`, so no snapshot was written to the live tree. `.sdlc/runtime/` already held `prune.json` and `prune.lock` before this step.
- No commit and no throwaway worktree.

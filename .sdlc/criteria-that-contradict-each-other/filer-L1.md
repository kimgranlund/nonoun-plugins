<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0062: Run (guard) criteria in `steps.py split --only N` and refuse on a red guard

## PR body
### Summary
`steps.py split --only N` now runs step N's `(guard)` criteria against the current tree before it writes that step's handoff. If a guard is red now or times out, the split refuses as a `plan defect`. A plan whose guard cannot pass is now caught before the build instead of by the verifier. The full `split` and `lint` still execute nothing, as the user decided. Contradicting criteria are still left to the planner prompt.

### Changes
- **`plugins/sdlc-lite/scripts/steps.py`** (step 1, builder L3):
  - Span extraction moved into a shared `line_spans`, so `command_spans` and the new `guard_spans` see the same spans.
  - Added `is_guard_line`, `guard_skipped`, `guard_cwd`, `run_guard` and `run_guards`. `guard_skipped` skips spans that reference `HEAD^1` or hold a `<placeholder>`.
  - Each guard runs with `bash -c --` and stdin from DEVNULL. It starts from the git toplevel of the task dir, or the task dir itself outside git.
  - Guards run in a new session. On timeout the whole process group is killed, so a pipeline grandchild cannot hang the call.
  - New option `--guard-timeout SECONDS`, default 300. It refuses a value that is not finite or is not above 0.
  - A red or timed-out guard makes the split exit 1 and write nothing. Stderr gets one line per red guard, then an indented tail of its output, then a last line `plan defect: step <n> red guard: <span>; replan this step (/chain 3)`. When several guards are red, that last line names each of them.
  - Guards run only with `--only`, after the lint, missing-step and superseded checks and before any write. The existing lint `PLAN_DEFECT` constant is unchanged.
  - Updated the usage docstring and added seven `(n)` selftest cases.
- **Docs and doc guard** (step 2, builder L2):
  - `CLAUDE.md`: the steps.py Layout bullet, the Systems line (now three code gates) and the plan-defect decision describe the guard run.
  - `.claude/agents/sdlc-lite-author.md`: the plan-defect route names the `split --only` red guard as a source.
  - `skills/chain/SKILL.md`: item 4.2 describes the guard run and the red-guard refusal. Section 3 notes that the full split executes nothing.
  - `scripts/check.py`: added `'red guard'` to `PLAN_DEFECT_DOCS`.

### Verification
- **Step 1: pass (verifier L2, Fable medium).** All nine criteria passed.
  - Red-guard refusal, timeout refusal, the `--help` text, at least 6 `(n)` selftest cases (7 present) and the docstring words were each red at HEAD in a throwaway worktree and green after the change.
  - The guard "full split and lint execute nothing" was shown to bite: changing the `if only:` gate to `if True:` turned it red.
  - The skip guard was shown to bite: forcing `guard_skipped` to return `False` turned it red.
  - `sleep 30 | cat` with `--guard-timeout 1` refused in 1.23s, which confirms the process-group kill.
  - The guard's cwd was confirmed to be the git toplevel.
  - `steps.py selftest` and `scripts/check.sh` both passed.
- **Step 2: pass (verifier L1, Sonnet medium).** All six criteria passed. Each grep was red at HEAD. The phrases check.py already guards (`plan defect`, `Plan review`, `no new findings`) are intact. `steps.py selftest` and `check.sh` both passed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `steps.py split --only N` now runs the step's `(guard)` criteria first. It skips `HEAD^1` and `<placeholder>` spans, runs each guard under `--guard-timeout` (default 300s) from the git toplevel, and refuses with a `plan defect:` line on a red or timed-out guard. The full `split` and `lint` still execute nothing. (T-0062)

## Follow-ups
- Guards in `steps.py split --only N` really execute, so a `(guard)` criterion with side effects now changes the tree before the build; only the planner prompt forbids that, and no code check does.

<!-- role=planner level=L1 model=sonnet effort=medium -->
Nothing edited; I'm the read-only planner. I've read the code and the plan is below.

## Goal
Define `step-<n>.superseded-<k>/` as the name for a step dir replaced by a replan. `board.py` and `bench-summary.sh` skip it when counting steps, but still count its cost, and `/chain` and `handoff-format` document and perform the rename.

## Step 1: board.py ignores superseded dirs, with selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Add a helper `live_step_dirs(task)`. It returns `task.glob('step-*')` entries that are dirs and match `re.fullmatch(r'step-\d+', d.name)`.
- Use the helper in `plan_steps` (~line 109). Sort by `int(d.name[5:])` and keep the existing filter on `handoff.md` existing. The later `int(d.name.split('-')[1])` at ~line 118 stays valid for live dirs.
- Use the helper in the `--summary` L5 check (~line 170), replacing `t.glob('step-*/builder-L5.*')` with a check over live dirs.
- Leave `cost()` (line 54) and `has_step_work` (line 190) on the `step-*` glob. Superseded dirs still count for cost and recorded work. Add a short comment on each saying so.
- Update the module docstring (line 13) to mention that superseded dirs are ignored.

Add a selftest case in the same file, following the existing `expect(...)` style near line 410:
- Build a task with `step-1/handoff.md`, `step-2/handoff.md`, and `step-2.superseded-1/handoff.md`. Give the superseded dir a `builder-L5.md` and a `runs.jsonl` line with `cost_usd`.
- Expect `plan_steps` to return exactly two steps.
- Expect the rendered board to have exactly two step rows.
- Expect `--summary` to show no `⚠ L5`.
- Expect `cost()` to include the superseded dir's cost.
- Expect `has_step_work` to be true for a task whose only handoff sits in a superseded dir.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` passes and includes the new superseded cases.
- Negative control: temporarily revert the helper in `plan_steps`. The new selftest case must then fail; restore it afterwards.
- Manual: create a temp `.sdlc/x/` with `step-1`, `step-2`, and `step-2.superseded-1` (each with `handoff.md`) and run `board.py --root <tmp>`. The output has exactly two step rows and no second "2." row.
- The existing board and tickets selftests still pass.

## Step 2: bench-summary.sh skips superseded dirs for steps, keeps their cost
level: L1
### Do
In `plugins/sdlc-lite/scripts/bench-summary.sh`, in the step loop at line 13:
- After the `[[ -d "$s" ]] || continue` check, add a skip for any dir whose basename does not match `^step-[0-9]+$`. For example, `[[ "$(basename "$s")" =~ ^step-[0-9]+$ ]] || continue`.
- Leave the cost line (20), which globs `step-*/runs.jsonl`, unchanged.
- Add a comment saying superseded dirs count for cost only.

### Acceptance criteria
- Build a temp bench dir with `results/2026-01-01-t/step-1/` (a passing `verifier-L1.md` and a builder `runs.jsonl` line with cost 1.00) and `results/2026-01-01-t/step-1.superseded-1/` (a builder `runs.jsonl` line with cost 2.00).
- Run `SDLC_BENCH_DIR=<tmp> plugins/sdlc-lite/scripts/bench-summary.sh`. The output shows steps=1, passed=1, attempts=1, cost=3.00.
- `shellcheck plugins/sdlc-lite/scripts/bench-summary.sh` is clean.

## Step 3: Document the name and perform the rename in /chain
level: L1
### Do
- In `plugins/sdlc-lite/skills/handoff-format/SKILL.md`:
  - Add `step-2.superseded-1/   a step replaced by a replan; ignored as a step, still counted for cost` to the layout block after `step-2/ ...` (~line 21).
  - Add one rule line: a live step dir is exactly `step-<digits>`; a replan renames replaced dirs to `step-<n>.superseded-<k>/` (k is the first free number); the board and scripts do not count these as steps.
- In `plugins/sdlc-lite/skills/chain/SKILL.md`, in step 4.2 (line 30):
  - Before "rewrite the remaining step handoffs", add that the conductor moves each `step-<n>/` with n at or above the blocked step that already holds builder or verifier output to `step-<n>.superseded-<k>/`, taking the first free k.
  - Then it writes fresh `step-<n>/handoff.md`.

### Acceptance criteria
- `grep -n 'superseded' plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/skills/chain/SKILL.md` shows the layout entry, the rule line, and the step 4.2 rename instruction.
- `plugins/sdlc-lite/scripts/check.sh` passes end to end, apart from the expected CLAUDE.md validate warning.

## Step 4: Audit the remaining step-* readers
level: L1
### Do
- Run `grep -rn 'step-' plugins/sdlc-lite --include='*.sh' --include='*.py' --include='*.md'`, excluding `bench/tasks` and `bench/results` fixtures.
- Confirm no unaddressed reader counts steps. Known remaining readers: `statusline.sh:46` (`step-[0-9]*` on a running-role path, which still names the step number), `board.py` `cost` and `has_step_work` (intentionally inclusive), and `tickets.py` (only fixture text).
- If the grep finds any other step counter in `bench.sh` or `skills/*`, make it skip superseded dirs.
- Update the `plugins/sdlc-lite/CLAUDE.md` Layout or board line if it describes step globbing. Also keep the `sdlc-lite-author` agent in sync only if it mentions step dirs.

### Acceptance criteria
- The grep output was reviewed and each hit is either a live-step-only reader, an intentionally inclusive reader, or a fixture. Report any change made.
- `plugins/sdlc-lite/scripts/check.sh` passes.

## Risks
- I did not open the `bench.sh` sources, `skills/bench`, or `skills/chain` beyond line 30. Step 4's audit covers them, but a step counter using a non-`step-` pattern (for example `ls -d */`) could exist.
- `plan_steps` falls back to the planner file when no live `handoff.md` exists. A task whose only step handoffs are superseded then renders from the newest plan. I think that is intended.
- Existing hand-renamed dirs like `step-15-blocked` stop rendering. This is accepted in the ticket's non-goals.

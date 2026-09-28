<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Decide the newest builder, verifier, planner, and filer result from the recorded run order in runs.jsonl, falling back to name order and never to mtime, so a fresh clone or checkout reads the same verdicts as the machine that ran them.

## Step 1: Shared ordering helper `order.py`, and run.sh records the result file
level: L3
### Do
- New module `plugins/sdlc-lite/scripts/order.py`. The other scripts import it (`board.py` already does `import tickets` from the same dir), and it also runs as a CLI. One ordering rule, written once:
  - `records(d)`: the lines of `d/runs.jsonl` in file order, with their index. Skip bad JSON lines. A missing file gives `[]`.
  - Rank of a result file (`<role>-L*.md` in `d`):
    1. A record with a `file` field (new, see below) ranks that file directly by its line index.
    2. Records without `file` (the legacy trail) are grouped by (role, level). They pair with that role-level's canonical files that are not already ranked. Canonical means the name matches `^<role>-(L\d)(?:-(\d+))?\.md$`, with no suffix meaning k=1. Pairing runs from the end: the last record goes to the highest k, and so on. This is needed because legacy trails have overwritten or hand-renamed files. In `bench/results/2026-09-24-button-geometry-model/step-2`, two verifier L2 runs left only `verifier-L2.md`, which is the later one.
    3. Anything else is unrecorded. That covers non-canonical legacy names like `verifier-L1.attempt2.md`, extra files, and dirs with no runs.jsonl.
  - Sort key: an unrecorded file sorts as `(0, level number, k, name)`, a recorded one as `(1, rank)`. Unrecorded files always sort before recorded ones.
  - Public API:
    - `ordered(d, role)`: the list from oldest to newest.
    - `newest(d, role)`: a path or None.
    - `counts_after(later, earlier)`: True when both are recorded and `rank(later) >= rank(earlier)`, and also True when either one is unrecorded. This keeps the current "a verifier with no records counts" behavior for fixtures.
  - No `stat()` / mtime anywhere in the module.
  - CLI:
    - `order.py newest <dir> <role>` prints the newest path, or nothing. Exit 0.
    - `order.py selftest`: every fixture file gets the same mtime (`os.utime`). At least one case also sets the mtimes inverse to the true order, so an mtime rule would give the wrong answer. Cases:
      - (a) records with `file`
      - (b) legacy records with no `file`, paired from the end (reproduces button-geometry step-2 so that `verifier-L2.md` is newest)
      - (c) no runs.jsonl: level then k then name
      - (d) `counts_after` true, false, and unrecorded
      - (e) bad JSON lines are skipped
- `plugins/sdlc-lite/scripts/run.sh`: the runs.jsonl `jq -c` line gains `file: "<name>.md"` (`--arg file "$name.md"`). Leave the verifier swap for Step 4.
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/order.py" selftest || fail=1`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: assert that each of the 3 runs.jsonl lines carries `file`, equal to `planner-L3.md`, `planner-L3-2.md`, and `planner-L3-3.md` in order.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/order.py selftest` exits 0.
- `grep -n "mtime\|stat()" plugins/sdlc-lite/scripts/order.py` prints nothing.
- Copy `plugins/sdlc-lite/bench/results/2026-09-24-button-geometry-model/step-2` to a temp dir and run `touch -t 202601010000` on every file in it. Then `order.py newest <tmp> verifier` prints a path ending `verifier-L2.md`, and `order.py newest <tmp> builder` prints one ending `builder-L3.md`.
- Negative control: temporarily change the sort key in the selftest copy (or a scratch copy of order.py) to `st_mtime`. The selftest then fails.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`. `jq -r .file` over its runs.jsonl gives the three names in order. Running it with the `file` field removed from run.sh makes it FAIL.

## Step 2: board.py reads verdicts through order.py
level: L2
### Do
- In `plugins/sdlc-lite/scripts/board.py`:
  - `by_level(d, role, 'md')` returns `order.ordered(d, role)`.
  - For `.running` files, sort by `(level number, name)`, with no mtime.
  - At line 93, the verifier-after-build test becomes `order.counts_after(verifies[-1], last_build)`.
  - `plan_steps` gets the newest plan through the same `by_level`.
  - Update the docstring line "the newest file by mtime wins" to state the runs.jsonl rule.
  - Leave the task-recency uses alone (`summary`'s task pick, and `sort_tasks`, including their selftests). They are display order, not verdicts.
- Add a board selftest case with equal mtimes on every file. Step dir with runs.jsonl records in this order:
  1. builder L1
  2. verifier L1 with `## Verdict` fail
  3. builder L2
  4. verifier L2 with `## Verdict` pass

  Expected row: 🟢 pass · builder L2 · verifier L2. Second fixture: the last record is a builder run after the passing verifier. Expected row: awaiting verify. Also include one fixture whose mtimes are inverse to the record order.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0.
- `grep -n "st_mtime" plugins/sdlc-lite/scripts/board.py` shows only the lines in `summary` (task pick), `sort_tasks`, and their selftest. None are in `by_level`, `step_row`, or `plan_steps`.
- Copy `bench/results/2026-09-24-button-geometry-model` into `<tmp>/results/`, `touch` every file to one time, and run `board.py --root <tmp>/results`. It shows step 2 as 🟢 pass · builder L3 · verifier L2.
- Negative control: reverting line 93 to the mtime comparison makes the new selftest case fail.

## Step 3: steps.py and tickets.py pick the newest planner and filer through order.py
level: L2
### Do
- `plugins/sdlc-lite/scripts/steps.py`:
  - `find_plan` uses `order.newest(target, 'planner')`, keeping the "no planner-*.md" Fail message.
  - Update the docstring and the argparse help ("by mtime").
  - Rewrite selftest case (c). Two planner files with equal mtimes plus a runs.jsonl that records the lower-named file last: that file is used. Add a variant with inverse mtimes that gives the same result. Also cover no runs.jsonl: level then k order, so `planner-L3.md` beats `planner-L2.md`.
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `filers = order.ordered(d, 'filer')` (line 465).
  - Rewrite selftest (h) the same way: equal mtimes, with runs.jsonl deciding the order. Include an inverse-mtime variant, and a fallback to name order when there are no records.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` and `python3 plugins/sdlc-lite/scripts/tickets.py selftest` both exit 0.
- `grep -n "st_mtime" plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/scripts/tickets.py` shows only steps.py's snapshot helper (about line 191, which checks that nothing was written) and no ordering use.
- Negative control: restoring the mtime key in `find_plan` or in tickets.py line 465 makes the rewritten (c) or (h) case fail.

## Step 4: run.sh verifier swap and bench-summary.sh use order.py
level: L2
### Do
- `plugins/sdlc-lite/scripts/run.sh`: replace `ls -t "$dir"/builder-L*.md | head -1` with `python3 "$plugin_root/scripts/order.py" newest "$dir" builder`. Keep `|| true` and an empty result meaning no build.
- `plugins/sdlc-lite/scripts/bench-summary.sh`: replace the `-nt` loop with `v=$(python3 "$root/scripts/order.py" newest "$s" verifier)`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: add a dry-run case (`SDLC_DRY_RUN=1`) in the throwaway repo, with a step dir holding:
  - `builder-L5.md` (header `model=fable`)
  - `builder-L1.md` (header `model=sonnet`)
  - equal mtimes
  - a runs.jsonl recording L1 first and L5 last

  Then `run.sh verifier L2` must print `--model opus` and `--effort medium`: Fable swapped to Opus, the effort left as is. Add the mirror case, where the records show L1 last, so verifier L1 (Sonnet) swaps to `--model opus --effort medium`, and verifier L2 stays `fable`.
### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`. Reverting the swap line to `ls -t` makes it FAIL.
- Copy `bench/results/2026-09-24-button-geometry-model` into `<tmp>/results/`, `touch` every file to one time, and run `plugins/sdlc-lite/scripts/bench-summary.sh --bench-dir <tmp>`. It reports `3` steps and `3` passed.
- `grep -nE "ls -t|-nt " plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/bench-summary.sh` prints nothing.
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/*.sh` is clean.

## Step 5: Docs say runs.jsonl order, not mtime
level: L1
### Do
Replace the mtime wording with the rule: "newest = latest runs.jsonl record (run.sh records `file`), else level then rerun index then name; never mtime".
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`:
  - line 27 ("the newest file by mtime is the current one")
  - line 16: the runs.jsonl fields now include `file`
- `CLAUDE.md` (repo root), Layout section:
  - mention `scripts/order.py` as the shared ordering rule, and that check.sh runs its selftest
  - note that runs.jsonl lines carry `file`
- `.claude/agents/sdlc-lite-author.md`: add the invariant that verdict and newest-file decisions go through `order.py` and never use mtime. Keep it in sync with CLAUDE.md.
- `plugins/sdlc-lite/skills/board/SKILL.md`: leave the `recent (mtime)` wording. It is task display order.
### Acceptance criteria
- `grep -rn -i "by mtime" plugins/sdlc-lite/skills plugins/sdlc-lite/agents plugins/sdlc-lite/scripts CLAUDE.md .claude/agents` returns only task-display-order text (board SKILL `--sort recent`, and board.py's `sort_tasks` docstring and selftest).
- `grep -n "order.py" CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` finds each file.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only validate warning is the expected one about CLAUDE.md.

## Risks
- runs.jsonl does not record the result file today. It has only ts, role, level, model, effort, cost, duration, and turns. Legacy trails depend on the pair-from-the-end guess. That guess matches button-geometry, but it can mislabel a trail where runs were deleted or files were renamed to canonical names by hand.
- Unrecorded files always sort before recorded ones. A result placed by hand next to a recorded trail will never count as newest.
- `counts_after` returns True whenever either file is unrecorded. A stale unrecorded verifier could still show pass over a newer recorded build.
- The ticket's Repro/Expected/Actual sections are empty. The review note is the only repro, and the acceptance checks use the committed button-geometry trail to stand in for it.

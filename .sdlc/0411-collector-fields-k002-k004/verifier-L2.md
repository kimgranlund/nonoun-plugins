<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 `fleet_collect.py selftest` prints `ok:` for each of the seven labels in Done when and exits 0: pass. Evidence: I ran Done-when checks c1, c2 and c3 on the built tree and all three gave `rc=0`. `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest` ends `fleet_collect selftest: ok`, rc=0. All seven `ok:` lines match exactly, and they include `ok: plan_defects: a refusals.jsonl line in the window is counted early` and `ok: attempts: completed verifier minutes run from started_at to finished_at`. At base 685f7048, in a throwaway worktree, c1, c2 and c3 each gave `rc=1`, so all three go red without the build. Mutation checks were run on a copy in the throwaway worktree, and each one turned its own label `FAIL`:
  - forcing `pid_alive` to always return False failed the orphaned label and the negative-control label;
  - forcing `result_blocked` to return False failed the results label;
  - setting `late += 0` failed the late label;
  - setting `early += 0` failed the early label;
  - disabling the next-start branch (`if later:` to `if False:`) failed the lost_min label;
  - dropping `done_min.append` failed the attempts label.
- #2 the new keys appear in `collect` output with the shapes in Intent, and every key present before is unchanged: pass. Evidence: I ran `fleet_collect.py collect /Users/kimgranlund/Projects/nonoun/sdlc-lite --since 2026-10-09` with both the built script and the base script and diffed the JSON.
  - Added top-level keys: `['results', 'plan_defects', 'attempts']`. None removed.
  - `runs.interrupted` gains only `lost_min_median` and `lost_min_total`. Each attempt gains `lost_min`. `runs.orphaned` is `{count, attempts:[{attempt_id, role, level, started_at, path}]}`.
  - After stripping the new subkeys, `runs`, `repo`, `window`, `plan_review_share`, `tickets`, `ci` and `summary` all read UNCHANGED against base.
  - The values match the planner's baseline recorded in the KPI docs, from a separate script (`kpi-baseline-probe.py`):
    - sdlc-lite: lost_min [10.7, 56.9, 71.4], orphaned 9, builder 0/0, late 0.
    - ui-kit-maison: lost_min {5.3, 41.0, 68.9, 5.3, 27.6}, orphaned 3, builder 1 of 23, late 6.
    - agent-ui: builder 2 of 12, late 2.
  - For a repo with no `.sdlc`, a selftest case asserts zero defaults (`results` {0,0}, `attempts` {by_role:{}}, `plan_defects` {0,0}). The no-interrupted case asserts a null median and a 0 total.
- #3 `fleet_detect.py selftest` and `fleet_status.py selftest` pass: pass. Evidence: guards g6 and g7 gave `rc=0` on the built tree and `rc=0` at base. `git grep -n "scan_sdlc\|collect_runs" -- plugins scripts` finds no caller outside `fleet_collect.py`, so the changed return tuple of `scan_sdlc` breaks no dependent. `collect_runs` only gained an optional `extra=None` keyword.
- #4 KPI files 002, 003 and 004 no longer contain `absent until plan step 1` or "cannot be read today", and 004 still says early reads 0 until step 5: pass. Evidence:
  - Done-when c4 gave `rc=0` on the built tree and `rc=1` at base.
  - `grep -n "cannot be read today" docs/kpi/00[234]-*.md` exits 1 (no match).
  - `docs/kpi/004-unsatisfiable-criteria-caught.md:12` reads `(early stays 0 until plan step 5 records refusals)`, and its Reading it says "Until step 5 lands, early reads 0 and the KPI reads 0".
  - No em or en dash appears in the added lines of `plugins` or `docs` (grep rc=1), and `git diff --check` gives rc=0.
- #5 only `fleet_collect.py` and the three KPI files changed outside `.sdlc`: pass. Evidence: guard g8 gave `rc=0`. The changed list it filters is exactly `docs/kpi/002-...md`, `docs/kpi/003-...md`, `docs/kpi/004-...md` and `plugins/sdlc-lite/scripts/fleet_collect.py`, with no untracked files outside `.sdlc`. As a negative control, I fed the same filter an extra `plugins/sdlc-lite/scripts/fleet_detect.py` line; it printed that line, so `test -z` would go red. Guard g5 (`fleet_collect.py selftest`) gave `rc=0` on both trees.

## Out of scope changes
- `.sdlc/0411-collector-fields-k002-k004/handoff.md` gained a `## Acceptance criteria` section. I read the diff: it appends lines only and changes no Done-when or Intent line. It sits under the `.sdlc` path that guard g8 excludes, so it is harmless.
- There is no `builder-*.md` in the artifacts dir. `runs.jsonl` shows this was the solo lane (role `solo`, `file` ""), so every claim above rests on my own runs, not on a builder report.
- One choice goes beyond the spec, but the spec does not forbid it. `orphaned` also skips a `running` record when another worktree copy of the same `attempt_id` is no longer running (`settled`, in `fleet_collect.py` `collect_runs`). Its selftest case covers it, and the numbers still match the baseline (sdlc-lite 9, maison 3).

## For the next attempt
None

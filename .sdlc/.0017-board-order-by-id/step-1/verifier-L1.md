<!-- role=verifier level=L1 model=sonnet effort=medium -->
All criteria verified with real command runs and a genuine red/green negative control. Diff is scoped to board.py and SKILL.md as required (the handoff.md edit predates this step, made by the planner).

## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0 and prints `board selftest: PASS`, including new sort cases: pass. Evidence: ran directly, output `board selftest: PASS`; confirmed the new case 6 exists in the diff (T-0002/T-0003, name-sort, mtime-order checks) and is exercised (verified via a red-then-green negative control below).
- Manually: `T-0003` dir newer by mtime than `T-0002` dir, `--sort id` lists `T-0002` before `T-0003`: pass. Evidence: built fixtures in a tmpdir with `T-0003-dir` older mtime and `T-0002-dir` newer, default (`recent`) order showed `T-0003` then `T-0002` (mtime-based), while `--sort id` showed `T-0002` then `T-0003` — a genuine divergence, not a same-order coincidence.
- `--sort name` lists folders in strict alphabetical order: pass. Evidence: tmpdir with `bravo`/`alpha`/`charlie` given out-of-order mtimes; `--sort name` output rows were `alpha`, `bravo`, `charlie`.
- No `--sort` flag produces output identical to pre-change (`recent`) behavior: pass. Evidence: default run above matched mtime order (oldest-first), consistent with the original `key=lambda d: d.stat().st_mtime` sort now wrapped in `sort_tasks(..., 'recent')` (`plugins/sdlc-lite/scripts/board.py` diff, `sort_tasks` fallback branch `return sorted(tasks, key=lambda d: d.stat().st_mtime)`).
- `plugins/sdlc-lite/skills/board/SKILL.md` has `--sort {recent,id,name}` in `argument-hint` and step 2 passes it through: pass. Evidence: `grep -n "argument-hint\|sort" plugins/sdlc-lite/skills/board/SKILL.md` → line 4 `argument-hint: [task] [--root DIR] [--sort {recent,id,name}]`, line 10 mentions passing `--sort <mode>` through.
- `scripts/check.sh` passes: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` → `ok: 18 role levels...`, `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- Negative control (checks-that-bite): pass. Evidence: in a throwaway `git worktree` copy of `board.py` with the id sort key mutated to `-int(m.group(1))`, selftest went RED (`board selftest: FAIL ... --sort id puts T-0002 before T-0003 ... got ['zulu-three', 'yankee-two', 'alpha', 'bravo']`, exit 1); restoring the real code made it GREEN again (`PASS`, exit 0). The selftest case genuinely discriminates on the id-sort mechanism, not a vacuous predicate.

## Out of scope changes
None. `.sdlc/0017-board-order-by-id/handoff.md` shows a diff but its mtime (16:16) predates the step-1 builder run (16:17–16:18); it was written by the planner filling in Intent/Constraints before dispatching this step, not touched by this step's builder. Builder-reported changes (`board.py`, `skills/board/SKILL.md`) match `git diff --stat` exactly.

## For the next attempt
None.

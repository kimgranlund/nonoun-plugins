<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- `steps.py selftest` exits 0 with an `ok:` line for each of (j), (k), (l), (m): pass. Evidence: `python3 plugins/sdlc-lite/scripts/steps.py selftest` → `rc=0`, stdout lines 16-22 are `ok: (j) ...` (four), `ok: (k) ...`, `ok: (l) ...`, `ok: (m) ...`, 22 ok lines total, ends `steps selftest: PASS`, stderr empty. Red at HEAD (throwaway worktree): the same run has 0 lines mentioning (j)-(m).
- Negative control with `lint_steps` stubbed exits 1 and stderr names (j) only: pass. Evidence: `cd plugins/sdlc-lite/scripts && python3 -c "import steps; steps.lint_steps = lambda *a, **k: []; raise SystemExit(steps.selftest())"` → `rc=1`; stderr lists three `(j)` checks (split refuses, lint on file, lint on task dir); `grep -o '([a-m])' | sort | uniq -c` → `3 (j)` and nothing else. The biting variable is `lint_steps` returning findings; (k), (l), (m) stay green as expected since they assert success paths.
- mktemp `BROKEN_PLAN` split prints `rc=1`, stderr has `plan defect` and `step 1`, no `step-1` written: pass. Evidence: command run verbatim → `rc=1`; `ls "$d"` → `handoff.md planner-L2.md`; stderr: `steps: .../planner-L2.md step 1: acceptance criterion command does not parse: grep -c 'foo' bar'`, two indented bash lines, `plan defect: replan this step (/chain 3)`. Red at HEAD: the same broken plan split with `rc=0` and wrote `step-1` and `step-2`.
- `steps.py lint .sdlc/0060-unpassable-plan-criteria/planner-L3.md` exits 0 printing `steps lint: ok`: pass. Evidence: output `steps lint: ok`, `rc=0`. Not vacuous: `command_spans` on that plan keeps 7 spans in step 1 and 8 in step 2, each passed through `bash -n`. At HEAD `lint` is an invalid choice (rc=2).
- `steps.py --help` lists `lint`: pass. Evidence: usage shows `{split,lint,selftest}` and a `lint  check that criterion commands parse under bash -n; writes nothing` line, `rc=0`. At HEAD: `grep -c lint` on help → 0.
- `grep -n 'scripts/steps.py' CLAUDE.md | grep -c 'plan defect'` prints 1, and `grep -c 'steps.py lint' plugins/sdlc-lite/skills/plan/SKILL.md` ≥ 1: pass. Evidence: outputs `1` and `1`; at HEAD both print `0`. CLAUDE.md:27 and SKILL.md:11 hold the text.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `rc=0`, tail shows `order selftest: PASS`, `run selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.

## Out of scope changes
`.sdlc/0060-unpassable-plan-criteria/handoff.md` is modified (a `## Plan review (conductor, before any build)` section). Its mtime is 07:58:51, before the builder run (steps.py 08:16, builder-L3.md 08:17), so it predates this step; the builder did not touch it. The four in-scope files (`steps.py`, `plan/SKILL.md`, `CLAUDE.md`) match the handoff. The rest of `git status` is task artifacts (planner results, runs.jsonl, step dirs). Throwaway worktree was created and removed; `git worktree list` shows only the two original trees.

## For the next attempt
None

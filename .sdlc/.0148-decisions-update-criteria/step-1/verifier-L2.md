<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Widening a `grep -vxF` scope criterion lets the widened file pass and a file outside the set still fails: pass. I ran the command in a throwaway repo and it exited 0. The span became `grep -vxF -e a.txt -e b.txt`. `b.txt` passed it and `c.txt` failed it. The `## Scope widened` item was written. The base steps.py has no `widen` (the `grep -cF 'ok: widen:'` count on its selftest was 0), so a run at base would go red.
- Widening a `grep -vxE` criterion escapes the path, so the widened file passes and a lookalike `bxtxt` still fails: pass. The command exited 0. The span became `grep -vxE "a\.txt|b\.txt"`, `b.txt` passed and `bxtxt` failed.
- A step with no scope criterion refuses with exit 1, a `plan defect:` last line and an unchanged handoff: pass. The command exited 0. stderr was `plan defect: steps widen refused: no criterion line has a command span ...; replan this step (/chain 4.2)`.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: widen:'`: pass. rc=0, and 21 `ok: widen:` lines are printed.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. It printed `steps selftest: PASS`, with rc 0 from the first pipeline element.
- `grep -qF 'widen <step dir>' plugins/sdlc-lite/scripts/steps.py`: pass. rc=0.
- `grep -qF 'widen <step dir>' docs/maintenance/sdlc-internals.md`: pass. rc=0.
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" ...; git ls-files --others ...; } | grep -vxE "plugins/sdlc-lite/scripts/steps.py|docs/maintenance/sdlc-internals.md" | { ! grep -q .; }`: pass. `SDLC_BASE_SHA` was e399089 and the check exited 0. It compares the tree with that sha and excludes `.sdlc`, so it can go red when another file changes. I did not separately run it red.

Extra checks beyond the criteria, all in throwaway repos:
- **A forms:** `grep -vE "^(a\.txt|d/e)$"` gained `b.txt` and `x\.y\+z` (path escaped). `grep -E -v "^(a\.txt)$"` gained `x\.y\+z`.
- **Rerun:** printed `widen: already applied` with rc 0.
- **Refusals:** two scope lines refused, and the handoff was unchanged. The bad paths `../x`, `/x`, `-x`, `a/../b` and `a b` each gave exit 1, the last line `plan defect: steps widen refused ...`, and an unchanged handoff.
- **Red span:** my test hit the lint refusal (a whole-tree diff criterion), not the red-span branch. That branch is covered by selftest case `widen: (c) a red new span`. I did not run it separately.
- **Repo checks:** `python3 plugins/sdlc-lite/scripts/check.py` exited 0. `git diff --check` was clean.

## Out of scope changes
`.sdlc/0148-decisions-update-criteria/handoff.md` is modified. It is under `.sdlc`, which the guard excludes, and it is the parent task's handoff, not a step deliverable. I checked `git diff --stat` and found no other files changed beyond `steps.py` and `sdlc-internals.md`.

## For the next attempt
None

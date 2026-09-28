<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py` (new, executable): `split <planner.md | task dir> [--only N ...]` and `selftest`, standard library only. Its style matches tickets.py: module docstring with usage, a `Fail` exception, `main(argv)`, and `sys.exit(main(sys.argv[1:]))`.

## Checks
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0. It printed 12 ok lines covering (a), (b) x2, (c), (d), (e), (f), (g) x2, (h) x2 and the overwrite case, then `steps selftest: PASS`.
- Negative control 1: changed `LEVEL_RE` to `r'.*'`. Selftest exited 1, with (d) as the failing case.
- Negative control 2: changed the refusal to `if False and done:`. Selftest exited 1, with both (g) cases failing.
- After each control I restored the file from a backup copy and the selftest exited 0 again. `git status` and `git diff --stat` then showed only `steps.py` as new under `plugins/`.
- Manual split on a temp copy of `.sdlc/.0025-bench-project-dirs` with its `step-*` dirs removed: exit 0 and two paths printed. I rebuilt each expected handoff separately with awk: "## Task goal", the Goal text from handoff.md, a blank line, then the planner slice from `## Step n:` up to the next `## ` line, trailing blanks trimmed. `diff` against the written file was empty for step-1 and step-2. Each file has one `level:` line.
- The same split on a temp copy that still has builder output: exit 1. The stderr message names `step-1.superseded-<k>/` and /chain 4.2. File mtimes before and after were identical, compared at both second and nanosecond precision (`stat -f %m` and `%Fm`).
- `git status --short`: nothing new under the real `.sdlc/`. The only entries there are the `.sdlc/0040-split-plan-into-steps/` changes that were already present before I started.
- `python3 -m py_compile plugins/sdlc-lite/scripts/steps.py`: passes.
- `grep -E '^(import|from) '`: lists only argparse, contextlib, io, os, pathlib, re, sys and tempfile.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (the tickets, board and run selftests, shellcheck, and plugin validate).

## Notes
- An empty `## Goal` section also fails. The spec only names a missing section; I treated an empty one as missing too.
- If the front matter opens with `---` and never closes, the script also fails.
- A missing target path fails, and so does a task dir with no `handoff.md`. The selftest covers the missing `handoff.md` under (h).
- When two `planner-*.md` files have the same mtime, the one with the later file name wins.
- `check.sh` does not run `steps.py selftest` yet. Adding it and wiring /chain to use the script are left for later steps.

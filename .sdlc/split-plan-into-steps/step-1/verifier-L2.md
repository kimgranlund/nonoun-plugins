<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- `steps.py selftest` exits 0 with an ok line for (a) through (h) plus overwrite: pass. Evidence: `python3 plugins/sdlc-lite/scripts/steps.py selftest` → 12 `ok:` lines covering (a), (b) x2, (c), (d), (e), (f), (g) x2, (h) x2, "re-split overwrites a plain step-1/handoff.md", then `steps selftest: PASS`, `rc=0`.
- Negative control (level regex accepts any line, or refusal skipped) makes the selftest exit nonzero; tree unchanged afterwards: pass. Evidence: run on throwaway copies of the script under mktemp, never editing the project file. NC1 `LEVEL_RE = re.compile(r'.*')` → rc=1, miss `(d) missing level:`. NC2 `if False and done:` → rc=1, misses both (g) cases. Extra NC3 (duplicate check disabled) → rc=1, miss (e). Extra NC4 (write a `leak` handoff before the refusal check) → rc=1, misses both (g) cases, proving the "writes nothing" snapshot bites. After the controls `git status --short plugins/` shows only `?? plugins/sdlc-lite/scripts/steps.py`; `git diff --stat plugins/` is empty.
- Manual split on a temp copy of `.sdlc/bench-project-dirs` (step dirs removed) exits 0 and each handoff matches the template and the planner slice: pass. Evidence: split printed two paths, `split rc=0`. step-1 and step-2 handoffs start with `## Task goal`, then "A project keeps its own bench tasks, results and logs, so a plugin update never removes them.", blank line, `## Step <n>:`; each has exactly 1 `level:` line (`grep -c`). Independently rebuilt expected files (Goal section from handoff.md + planner slice from `## Step n:` to the line before the next `## `, trailing blanks trimmed) and `diff` was empty for both ("diff step-1: identical", "diff step-2: identical"). Planner headings confirmed at lines 5, 41, 64 (`## Risks`).
- Same split against a copy whose step dirs hold builder output exits nonzero, names `superseded`, changes no mtimes: pass. Evidence: `refusal rc=1`; stderr: `steps: .../step-1 already holds role output (builder-L2.md, verifier-L1.md). Per /chain 4.2, rename it to step-1.superseded-<k>/ ...`; `stat -f '%Fm %N'` listing of all 12 files before and after: `diff` empty ("mtimes unchanged").
- `git status` shows no changes under the real `.sdlc/` from this step: pass. Evidence: `git status --short .sdlc` is identical before and after all runs; the entries present (`M .sdlc/split-plan-into-steps/handoff.md`, `?? planner-L2.md`, `runs.jsonl`, `step-1/`, `step-2/`) are the /chain task artifacts, all with mtimes 18:53:14 to 18:54:16, before the builder run started (~18:54:18 per `runs.jsonl`: end 01:55:55Z, duration 97.8s) and before `steps.py` (18:55:30).
- `py_compile` passes and imports are stdlib only: pass. Evidence: `python3 -m py_compile ... ; rc=0`. `grep -E '^(import|from) '` → argparse, contextlib, io, os, pathlib, re, sys, tempfile.
- Style and executability (from Do): pass. Evidence: `-rwxr-xr-x plugins/sdlc-lite/scripts/steps.py`; steps.py:2-15 module docstring with usage, :327 `def main(argv)`, :341 `sys.exit(main(sys.argv[1:]))`. `plugins/sdlc-lite/scripts/check.sh` rc=0 (tickets, board, run selftests, shellcheck, plugin validate).

## Out of scope changes
None. The only new file under `plugins/` is `scripts/steps.py`. The `.sdlc/split-plan-into-steps/` entries predate the builder run and belong to the chain itself.

## For the next attempt
None.

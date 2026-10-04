<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/validation/evals-live-run.md: new live-run record with Environment, Commands, Evidence and Limits sections.

## Checks
I ran all six arms in a `mktemp -d` copy made by rsync, then ran them again in a fresh copy. The results below are from the second run.
- Arm 1: `check.py plugins/sdlc-lite` gave exit 0 (`ok: 19 role levels, 9 agents checked`).
- Arm 2: after the `run.sh` builder:L2 edit and the matching level-rubric edit, `check.py` gave exit 1 with `FAIL evals: ... model table changed ...`.
- Arm 3: `evals.py lock --eval .sdlc/evals/0000-baseline.md` gave exit 1 with `is not later than`.
- Arm 4: `evals.py add live-probe ...` gave exit 0 and wrote `.sdlc/evals/0001-live-probe.md`. `evals.py lock` on that file gave exit 0, and `check.py` then gave exit 0.
- Arm 5: after changing the scout L1 effort in `models.json`, `check.py` gave exit 1 with `model table changed`.
- Arm 6: after `rm -rf "$T"`, `git diff --quiet $SDLC_BASE_SHA -- run.sh models.json` gave exit 0. `evals.py check` gave exit 0 and still cites 0000-baseline.
- Acceptance criteria 1 to 4 (doc strings grep, date grep, table-lock.json shape, `evals.py check`) all exit 0.
- Guards 5 and 6 (`run.sh`/`models.json` unchanged, allowed changed-file list) both exit 0.
- `git diff --check` exit 0. The doc has no em dashes.

## Notes
- In the first run, the `check.py` output redirect for arms 1 and 4 pointed at `/tmp/x`, which turned out to be an existing directory. Their exit codes were therefore invalid, so I reran every arm in a fresh copy. The doc says this.
- I did not touch `/tmp/x` or its contents. The cleanup `rm -f` failed on it because it is a directory.
- In arm 2, `check.py` printed one other FAIL line besides the evals one: the summary line `FAIL: 19 role levels, 9 agents checked`. That is the overall verdict line, not a second finding, and the doc records it.

<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: `step_row` now shows a builder Status that starts with `inherited red` as `🔴 inherited red · builder <level>, ask the user`. The module docstring's Status paragraph describes this, and section 7 has a new `step_fixture` selftest case whose expect label contains `inherited red`.

## Checks
- Criterion 1 (the `mktemp` fixture plus the `python3 -c` call to `step_row`), run from the repo root: exit 0.
- `grep -q 'inherited red' plugins/sdlc-lite/scripts/board.py`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`: exit 0, prints `board selftest: PASS`. The first attempt failed only because my redirect target `/tmp/x` is a directory. The rerun without the redirect passed.

## Notes
`git diff --stat` also shows changes to `.sdlc/builder-inherited-red/handoff.md`, `run.sh`, `run-selftest.sh` and `steps.py`. They were already in the tree before this step and I did not touch them.

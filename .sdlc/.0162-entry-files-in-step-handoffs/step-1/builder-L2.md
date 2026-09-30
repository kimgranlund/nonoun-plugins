<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added the `read_first_paths` helper. `lint_steps` now checks each `### Read first` path against the git toplevel of the plan file's folder, or that folder when outside git. The `lint` and `split` docstrings are updated, and selftest case (r) is added.
- `docs/maintenance/sdlc-internals.md`: the `scripts/steps.py` entry now describes the `### Read first` path check.

## Checks
- Acceptance criterion 1 (a temp git repo with `ok.md` and `bad.md`): passed (exit 0). `ok.md` printed `steps lint: ok`. `bad.md` exited 1, named `gone/AGENTS.md` and ended with `plan defect: replan this step (/chain 3)`.
- `steps.py selftest`: rc 0, `steps selftest: PASS`.
- The three `grep -qF 'ok: (r) ...'` selftest criteria all exited 0.
- `grep -qF '### Read first' plugins/sdlc-lite/scripts/steps.py`: exited 0.
- `grep -qF 'Read first' docs/maintenance/sdlc-internals.md`: exited 0.
- `git diff --check`: clean.
- `python3 plugins/sdlc-lite/scripts/check.py`: ok (18 role levels, 8 agents checked).

## Notes
- The path is the text of the first code span on each `-` or `*` list item.
- The toplevel is looked up once per plan, and only when some step has a `### Read first` subsection.
- `swap` and the `split` copy logic are unchanged. The (r) case also shows that `split` refuses a missing path.

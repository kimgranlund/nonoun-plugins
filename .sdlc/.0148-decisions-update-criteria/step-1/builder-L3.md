<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added the `widen` subcommand, built from `swap`'s helpers: `ere_escape`, `widen_forms`, `widen_listed`, `widen_span`, `replace_span`, `add_scope_widened`, `widen` and `cmd_widen`. Also added the argparse subparser, the `widen <step dir> ...` usage and entry in the module docstring, and 25 selftest cases prefixed `widen:`.
- `docs/maintenance/sdlc-internals.md`: documented `widen <step dir> <path> [<path> ...] [--timeout SECONDS]` in the `scripts/steps.py` entry.

## Checks
- Criterion 1 (the F form in a throwaway repo): rc 0. b.txt passes the widened span, c.txt fails it, and the `## Scope widened` item is written.
- Criterion 2 (the E form, `bxtxt` lookalike): rc 0. The new span is `grep -vxE "a\.txt|b\.txt"`.
- Criterion 3 (no scope criterion): rc 0. Exit 1, the last stderr line starts with `plan defect:`, and the handoff is unchanged.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: widen:'`: rc 0.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: rc 0, `steps selftest: PASS`.
- `grep -qF 'widen <step dir>' plugins/sdlc-lite/scripts/steps.py`: rc 0.
- `grep -qF 'widen <step dir>' docs/maintenance/sdlc-internals.md`: rc 0.
- (guard) scope criterion, with `SDLC_BASE_SHA` from `step-1/base-sha` (e399089): rc 0.
- Negative control: a copy of steps.py with ERE escaping turned off makes the selftest exit 1, failing only the E-form and A-form `(a)` cases. The copy was in a mktemp dir and has been removed.
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0.
- `git diff --check`: clean.
- `steps.py widen --help`: rc 0. `steps.py next <dir> --bogus` still stops with argparse's "unrecognized arguments" error, rc 2.

## Notes
- **How `-x` reaches the refusal:** `main` now uses `parse_known_args` so that a path like `-x` gets `widen`'s plan-defect refusal rather than an argparse usage error. The leftover arguments are treated as paths only for `widen`. Every other subcommand still stops on unknown arguments, as before.
- **What counts as a scope line:** a criterion list item with a command span that holds `git diff --name-only` and any inverted grep (`-…v` or `--invert-match`). The outcomes:
  - No such line: refused.
  - Two or more such lines: refused.
  - One such line whose span has none of the F, E or A forms: refused as unrecognized.
  - One such line whose span has more than one form: refused.
- **Repeated paths:** duplicate path arguments are collapsed. On a partial rerun only the unlisted paths are added and recorded, and the existing `## Scope widened` section keeps its earlier items.
- **Selftest coverage beyond the handoff:** besides cases (a) to (d), the selftest also covers a second widen on the same step, a span that changes the work tree, a missing handoff, no path given, bad paths `a b` and `x/../y`, and a control where `base-sha` is missing, so HEAD is used and the span is red.

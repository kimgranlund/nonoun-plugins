<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/onboard.py` (new, executable): contains `LayoutError`, `Layout`, `parse_layout`, `frozen_match`, `scan_lines`, `has_import`, the gate-based `selftest`, and an argparse CLI with `setup [--dry-run] [--force]`, `check`, and `selftest`. `setup` and `check` print "not implemented" and exit 2.

## Checks
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: exit 0. Printed `gate layout-parsing: positive ok, negative ok` and `gate import-detection: positive ok, negative ok`. The interpreter was Python 3.9.6.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qF "gate layout-parsing: positive ok, negative ok"`: exit 0.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qF "gate import-detection: positive ok, negative ok"`: exit 0.
- `onboard.py setup` and `onboard.py check`: each printed "not implemented" and exited 2.
- In-process check of the FAIL path: I passed the defective `has_import` in as the real implementation and the real one as the defect. It printed `gate import-detection: FAIL positive failed: ...; negative (real) was not rejected` and exited 1.
- In-process probe of `frozen_match`: 12 cases passed. They cover a folder pattern with a trailing `/`, `*` staying inside one segment, `**` and `**/` crossing segments, a leading `./`, and a near-miss prefix (`docs/reportsX`).
- `git diff --check`: clean.

## Notes
- The design gives no defective code variant for the layout-parsing gate; its negatives are bad input files. To match the gate structure in the handoff, the gate runs against three parser variants: one skips the list-line form rule, one skips the duplicate-heading rule, one skips the duplicate-home rule. "negative ok" means every variant was rejected. A variant that crashes is reported as FAIL and does not count as a rejection.
- Choices the grammar leaves open:
  - Lines inside a code fence are skipped by the layout parser.
  - A heading of level 1 or 2 other than the two section headings ends the current section. Deeper headings do not.
  - A list marker needs whitespace after it before the backticked form.
  - A missing heading is reported at the file's last line, or line 1 if the file is empty.
  - `has_import` does not accept a line with leading spaces, which is the "exactly" in the spec.
  - Lines that open or close a fence count as inside the fence.
- `frozen_match` treats `?` and other characters literally. Only `*` and `**` are wildcards.
- `frozen_match` has no selftest gate in this step and was checked only by the in-process probe above.

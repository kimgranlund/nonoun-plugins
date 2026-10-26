# Claude returned-output truncation markers

## Added

- Regression coverage for Claude string and text-block-list results, with negative controls for call arguments, non-result blocks and ordinary prose.

## Changed

- None of the skill entry, workflow or historical evidence files changed.

## Fixed

- The existing explicit-output-marker detector now recognizes `[N characters truncated]` in Claude returned tool blocks. It retains output-only attribution and the existing statement that downstream harm is unproven.

## Open

- Marker detection cannot establish that omitted content caused a product failure, nor detect silent truncation. The four historical entry reads were reported recovered by subsequent reads.

## Verification

- `python3 -B -m unittest discover -s tests`: 51 tests pass.
- Reanalysis of four existing historical hydrated traces detects exactly one clipped return each, at source trace lines 19, 19, 20 and 20. Source SHA256 digests unchanged. No new builder trial.
- Durable bounded evidence: `/Users/kimba/Projects/differential-ui/evidence/0220-routing-verification-repair/claude-truncation/reanalysis.json`.

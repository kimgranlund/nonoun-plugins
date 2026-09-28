<!-- role=filer level=L1 model=sonnet effort=medium -->
All steps verified pass. Ready to draft the filer output.

## Warnings
None

## PR title
T-0122: fanout.py inherited_red reads verifier tests when the verifier is the newer inherited-red source

## PR body
Summary: `fanout.py`'s `inherited_red()` previously always read the reported tests from the newest builder's `## Status` line, so a step that was inherited-red because the *verifier's* Verdict said so (newer than the builder result) wrongly reported the builder's Status text (e.g. `done`) instead of the actual tests.

Changes:
- `plugins/sdlc-lite/scripts/fanout.py`: `inherited_red()` now picks its source by `len(read)` (the list `steps.next_action` returns): `len(read) == 1` (builder-inherited) still reads `## Status` from `read[0]`; `len(read) == 2` (verifier-inherited) reads `## Verdict` from `read[1]` via `steps.section(read[1], 'Verdict')`, applying the same `inherited red:` prefix strip.
- Updated `inherited_red()`'s docstring, the module docstring's step-3 description, and the selftest module docstring to describe both sources.
- Added selftest case 5c: builder `## Status` `done` plus a newer verifier `## Verdict` `inherited red: test_v` must give the outcome `inherited red: step-1: test_v`, not `done`.
- No other files changed; nothing committed.

How verified: builder L2 (Opus low) implemented the fix and ran the acceptance criteria plus `scripts/check.sh` (exit 0, all selftests including fanout, shellcheck, plugin validate). Verifier L1 (Sonnet medium) independently reproduced every criterion in the built tree, confirmed criterion 1 was red before the fix in a throwaway worktree at pre-build HEAD, confirmed the builder-inherited guard path stays green both before and after, and mechanically reverted just the fix hunk in a separate throwaway worktree to prove the new selftest case 5c actually fails without the fix (not vacuous). Verdict: pass on all criteria, docstring updates, and scope (only `fanout.py` modified, nothing committed).

## Changelog entry
Fixed: `fanout.py` now reports the verifier's tests (not the builder's Status text) when a lane step is inherited-red because the verifier's Verdict, not the builder's Status, carried the inherited-red result.

## Follow-ups
None

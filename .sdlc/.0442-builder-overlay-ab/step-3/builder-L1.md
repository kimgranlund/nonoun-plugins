<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/i/docs/reports/2026-10-11-builder-overlay-ab.md`: replaced "The clones are kept there." in the Arm roots bullet with a sentence saying the clones and the evidence folder were removed with the tmp prefix when `dispatch.py record` recorded the builder run. It adds that the hidden_check and minutes columns therefore cannot be re-observed and stand as recorded claims.

## Checks
- The (red) criterion command passed: "The clones are kept there." is gone and "removed" is present.
- `git diff --check 27130b4a5f929aee1447319a0359d85751bd3a98` printed nothing, so it is clean.

## Notes
- The red checkpoint recorded only as a retrospective control. `redck` found 4 source paths already different from the base, because the tree already held uncommitted work from other steps. I ran it before my edit, but it is not stored as a red-before-edit record.
- Beyond the Arm roots sentence, the working tree still holds changes from other steps that I did not touch.

## Task goal
A dated report with a keep, extend or drop verdict backed by priced runs.

## Step 3: Loose ends
level: L1
### Read first
- `docs/reports/AGENTS.md`
### Do
In `docs/reports/2026-10-11-builder-overlay-ab.md`, Method section, the "Arm roots" bullet ends with "The clones are kept there." That is false: `dispatch.py record` removed the dispatch tmp prefix `.worktrees/tmp/0442-s2-builder-L3/` (arm clones, cell clones, evidence) after the report was written. Replace that sentence with one stating the clones and the evidence folder were removed with the tmp prefix when the builder run was recorded, so the hidden_check and minutes columns cannot be re-observed and stand as recorded claims. Change nothing else.
### Acceptance criteria
- (red) `! grep -qF "The clones are kept there." docs/reports/2026-10-11-builder-overlay-ab.md && grep -qiE "removed" docs/reports/2026-10-11-builder-overlay-ab.md`
- (guard) `git diff --check "$SDLC_BASE_SHA"`

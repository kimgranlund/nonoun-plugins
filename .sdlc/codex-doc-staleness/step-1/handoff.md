## Task goal
Current docs describe the Codex alternate verifier map, agent count, and scout model as they are now; dated records stay history.

## Step 1: Fix four stale statements
level: L1

### Do
1. In `docs/codex-role-execution.md`, replace the sentence "The current alternate pairs `gpt-6-astra` builders with `gpt-6.1-sol` verifiers at the verifier’s configured effort; other role defaults stay as listed above." with: "The current alternates map `gpt-6-luna` and `gpt-6-astra` to `gpt-6.1-sol`, so a verifier that would share its builder's model runs on `gpt-6.1-sol` at the verifier's configured effort. With the default allocation the only builder and verifier pair that shares a model is builder L1 and verifier L1, both Luna; other role defaults stay as listed above."
2. In `docs/codex-role-execution.md`, in the sentence "This smoke test predates the current `gpt-6-astra` → `gpt-6.1-sol` mapping described above.", replace "the current `gpt-6-astra` → `gpt-6.1-sol` mapping described above" with "the alternate mapping described above".
3. In `plugins/sdlc-lite/HARNESS-NOTES.md` line 19, replace "This installs 19 namespaced agents (18 role levels and conductor, plus one alternate verifier profile per entry configured in `verifier_alternates`)" with "This installs 19 namespaced base agents (18 role levels and conductor) plus one alternate verifier profile for each verifier level whose model has an entry in `verifier_alternates`, 22 with the default configuration,". Keep the rest of the sentence and line unchanged.
4. In `docs/reports/release-0.19.0.md`, directly after the existing "Correction, 2026-09-30" line under the first Known limits bullet, add an indented line: "  Later the same day the scout moved to `gpt-5.6-terra` low under the user's Claude-tier mirror; the current mapping is in `docs/codex-role-execution.md`." Do not change the existing correction line.

### Acceptance criteria
- `grep -qF "so a verifier that would share its builder's model runs on" docs/codex-role-execution.md`
- `grep -qF "predates the alternate mapping described above" docs/codex-role-execution.md`
- `grep -qF "22 with the default configuration" plugins/sdlc-lite/HARNESS-NOTES.md`
- `grep -qF "Later the same day the scout moved to" docs/reports/release-0.19.0.md`
- `! grep -qF "The current alternate pairs" docs/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

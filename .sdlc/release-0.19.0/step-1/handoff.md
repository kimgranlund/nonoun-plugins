## Task goal
Independent check that branch `release-0.19.0` is fit to release as SDLC Lite 0.19.0 and Progressive Context 0.1.2.

## Step 1: Release check
level: L3

### Do
Verify the release as a whole, not one step. Beyond the criteria below, read `docs/validation/release-0.19.0.md` and check each claim in its table against the commits since `cd6db5c` and the closed ticket folders under `.sdlc/` (the `.NNNN-` folders for T-0160, T-0162, T-0163, T-0164, T-0165, T-0168): that each change exists in the code, that each ticket's step folders hold a builder result and a passing verifier result, and that the known limits are stated truthfully. Check that both hosts' manifests for each plugin carry the same version, and that the new `onboard` skill and the changed conductor, planner, builder, and verifier bodies are consistent with each other and with `docs/repo-onboarding/design.md`. Report any claim in the release record that the evidence does not support.

### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `test "$(grep -h '"version"' plugins/sdlc-lite/.claude-plugin/plugin.json plugins/sdlc-lite/.codex-plugin/plugin.json | sort -u | wc -l)" -eq 1`
- (guard) `grep -q '"version": "0.19.0"' plugins/sdlc-lite/.claude-plugin/plugin.json`
- (guard) `git diff --check main -- . ":(exclude).sdlc"`

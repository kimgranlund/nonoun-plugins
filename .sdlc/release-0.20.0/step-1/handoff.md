## Task goal
Independent check that branch `release-0.20.0` is fit to release as SDLC Lite 0.20.0, with Progressive Context unchanged at 0.1.2.

## Step 1: Release check
level: L3

### Do
Verify the release as a whole, not one step. Beyond the criteria below, read `docs/reports/release-0.20.0.md` and check each claim in its table and in Upgrading and Known limits against the commits since `89e7ab8`, the closed ticket folders under `.sdlc/`, and the code: that each change exists, that each listed ticket's step folders hold a builder result and a passing verifier result, that the Codex mapping in `adapters/codex/models.json` matches what the record says, that no Claude model or effort in `scripts/run.sh` changed except the additions the record lists, and that Progressive Context truly has no change since 0.19.0. Check both hosts' manifests carry the same version for each plugin. Exercise the new `plan-reviewer` gate in a throwaway repository: `steps.py review` and `steps.py split` before and after a reviewer result that says `replan`. Report any claim the evidence does not support.

### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `test "$(grep -h '"version"' plugins/sdlc-lite/.claude-plugin/plugin.json plugins/sdlc-lite/.codex-plugin/plugin.json | sort -u | wc -l)" -eq 1`
- (guard) `grep -q '"version": "0.20.0"' plugins/sdlc-lite/.claude-plugin/plugin.json`
- (guard) `grep -q '"version": "0.1.2"' plugins/progressive-context/.claude-plugin/plugin.json`
- (guard) `git diff --check main -- . ":(exclude).sdlc"`

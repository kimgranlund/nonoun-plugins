## Task goal
Independent check that branch `release-0.20.1` is fit to release as SDLC Lite 0.20.1, with Progressive Context unchanged at 0.1.2.

## Step 1: Release check
level: L3

### Do
Verify the release as a whole. Read `docs/validation/release-0.20.1.md` and check each claim in its table, Upgrading and Known limits against the commits since `6803899`, the closed ticket folders `.sdlc/.0172-*` and `.sdlc/.0173-*`, and the code. Specifically: that the only model or effort changes in `scripts/run.sh` since `6803899` are the `scout:L1` and `planner:L3` rows; that `adapters/codex/models.json` is unchanged; that the level rubric, `check.py` and the selftest agree with `run.sh`; that the generated Codex agent changes are exactly the profiles that embed the level rubric; that Progressive Context has no change; and that both hosts' manifests carry the same version for each plugin. Reproduce the three probes in `docs/validation/haiku-alias-2026-09-30.md` (`claude -p --model haiku`, `--model claude-haiku-4-5`, `--model claude-haiku-5-5`, each with `--tools ""`, reading `modelUsage` from `--output-format json`) and say whether they match. Reproduce, with `SDLC_DRY_RUN=1`, the `run.sh` command lines for `scout L1`, `planner L3`, and `plan-reviewer L1` after a newest planner result whose header says `model=opus`. Inject a defect into a throwaway copy of `check.py` and of the rubric row to show the scout and planner L3 comparison can fail. Report any claim the evidence does not support, including any statement that implies a cost saving or a quality equivalence that was not measured.

### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `test "$(grep -h '"version"' plugins/sdlc-lite/.claude-plugin/plugin.json plugins/sdlc-lite/.codex-plugin/plugin.json | sort -u | wc -l)" -eq 1`
- (guard) `grep -q '"version": "0.20.1"' plugins/sdlc-lite/.claude-plugin/plugin.json`
- (guard) `grep -q '"version": "0.1.2"' plugins/progressive-context/.claude-plugin/plugin.json`
- (guard) `git diff --check main -- . ":(exclude).sdlc"`

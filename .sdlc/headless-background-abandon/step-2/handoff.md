## Task goal
A headless session (claude -p: bench, dogfood, fanout lanes, every role run) can never background a role run or a gate and then end its turn.

## Step 2: Set SDLC_HEADLESS=1 in headless launchers, guard the docs, bump version
level: L2
### Do
- `plugins/sdlc-lite/scripts/bench.sh`: add `SDLC_HEADLESS=1` to the env prefix of the `claude -p` call, next to `BASH_DEFAULT_TIMEOUT_MS`. Update the header comment.
- `plugins/sdlc-lite/scripts/fanout.py`: add `SDLC_HEADLESS='1'` to the driver `env` dict in the per-ticket function, next to `BASH_DEFAULT_TIMEOUT_MS`. Mention it in the docstring's driver env list (step 2). In the selftest `STUB`, fail when it is missing, for example `[ "${SDLC_HEADLESS:-}" = 1 ] || { echo "SDLC_HEADLESS not set" >&2; exit 1; }` near the top. `fanout.py selftest` then proves the driver gets it.
- Docs: in the headless sentence of `skills/chain/SKILL.md`, `skills/bench/SKILL.md`, `skills/fanout/SKILL.md`, and `agents/conductor.md` (all under `plugins/sdlc-lite/`), say that `hooks/block-background.sh` denies `run_in_background` whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`. Say that bench.sh and fanout set `SDLC_HEADLESS=1`, and that any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself. Keep every word the existing long-run check in `scripts/check.py` requires.
- `plugins/sdlc-lite/scripts/check.py`: add `'SDLC_HEADLESS'` to the required words of the long-run doc check, so those four files must keep naming it.
- Repo-root `CLAUDE.md`: in Layout, describe `hooks/block-background.sh` next to `hooks/block-publish.sh`: when it fires, what it tells the model, and the `SDLC_HEADLESS=1` convention for headless launchers. Add `hook-selftest.sh` to the check.sh list in Commands. Mirror the hazard in `.claude/agents/sdlc-lite-author.md`: headless means foreground, now enforced by the hook.
- Bump `plugins/sdlc-lite/.claude-plugin/plugin.json` version to `0.8.2`.
### Acceptance criteria
- `grep -q 'SDLC_HEADLESS=1' plugins/sdlc-lite/scripts/bench.sh`
- `python3 -c "import sys; s=open('plugins/sdlc-lite/scripts/fanout.py').read(); stub=s.split(\"STUB = r'''\")[1].split(\"'''\")[0]; sys.exit(0 if 'SDLC_HEADLESS' in stub else 1)"`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS` (the driver env must now carry `SDLC_HEADLESS`, or the stub fails)
- `test "$(grep -l SDLC_HEADLESS plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/skills/bench/SKILL.md plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/agents/conductor.md | wc -l)" -eq 4`
- `grep -q "SDLC_HEADLESS" plugins/sdlc-lite/scripts/check.py`
- `grep -q 'block-background' CLAUDE.md && grep -q 'SDLC_HEADLESS' CLAUDE.md && grep -q 'SDLC_HEADLESS' .claude/agents/sdlc-lite-author.md`
- `grep -q '"version": "0.8.2"' plugins/sdlc-lite/.claude-plugin/plugin.json`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0
- Observable: after the step, deleting `SDLC_HEADLESS` from one of the four docs makes `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` report a long-run missing-word error. The verifier checks this by reading the check.py diff, not by editing the tree.

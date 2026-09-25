<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make the plugin's PreToolUse(Bash) hook refuse `run_in_background: true` whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`. Then set `SDLC_HEADLESS=1` in every headless launcher (bench.sh, fanout.py's lane driver) and document it, so a headless session can never start a role run or gate in the background and then end its turn.

## Step 1: Hook that denies background Bash in headless sessions, with its selftest
level: L2
### Do
- Add `plugins/sdlc-lite/hooks/block-background.sh` (executable, `#!/usr/bin/env bash`). It reads the hook JSON from stdin with `jq`. It exits 0 unless both of these hold: `SDLC_ROLE` is non-empty or `SDLC_HEADLESS` is `1`, and `.tool_input.run_in_background == true`. When both hold, it prints this message to stderr and exits 2: "headless session (sdlc role '<role>' or SDLC_HEADLESS=1): run this in the foreground with the Bash timeout at 600000 or more; do not use run_in_background, and never end the turn while it runs, because that ends the session and abandons the work". The words `foreground` and `600000` must appear. `run_in_background` false, absent, or null must pass (exit 0), whatever the command is.
- Register it in `plugins/sdlc-lite/hooks/hooks.json` as a second command hook under the existing `"matcher": "Bash"` PreToolUse entry. Use the same `"${CLAUDE_PLUGIN_ROOT}/hooks/..."` quoting style. Keep `block-publish.sh` unchanged.
- Add `plugins/sdlc-lite/scripts/hook-selftest.sh`. It runs both hooks with fixture JSON on stdin and a controlled env, and never inherits the caller's `SDLC_ROLE`/`SDLC_HEADLESS`: use `env -u SDLC_ROLE -u SDLC_HEADLESS ...` as the base, because builders and verifiers run check.sh with `SDLC_ROLE` set. Cases:
  - SDLC_ROLE set + background true → 2, and stderr names foreground and 600000.
  - SDLC_HEADLESS=1 + background true → 2.
  - Neither set + background true → 0 (negative control).
  - SDLC_ROLE set + background false → 0.
  - SDLC_ROLE set + background absent → 0.
  - SDLC_HEADLESS=0 + background true → 0.
  - block-publish.sh still exits 2 on a push command with SDLC_ROLE set, and 0 on `ls`. Build the push string at runtime, for example `printf 'git %s' push`, so the live hook does not block the selftest's own Bash call.

  It prints `hook selftest: PASS` or `hook selftest: FAIL: <case>` and exits non-zero on failure, in the style of `scripts/run-selftest.sh`.
- Wire it into `plugins/sdlc-lite/scripts/check.sh` next to `run-selftest.sh` (`bash "$root/scripts/hook-selftest.sh" || fail=1`). Update the check.sh header comment.
### Acceptance criteria
- `test -x plugins/sdlc-lite/hooks/block-background.sh`
- `out=$(printf '%s' '{"tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_HEADLESS SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-background.sh 2>&1); test $? -eq 2 && grep -q 600000 <<<"$out" && grep -qi foreground <<<"$out"`
- `printf '%s' '{"tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_ROLE SDLC_HEADLESS=1 plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh` exits 0 (negative control; red now only because the file is missing)
- `printf '%s' '{"tool_input":{"command":"sleep 1"}}' | env -u SDLC_HEADLESS SDLC_ROLE=verifier plugins/sdlc-lite/hooks/block-background.sh` exits 0
- `grep -q 'hooks/block-background.sh' plugins/sdlc-lite/hooks/hooks.json && jq -e '.hooks.PreToolUse[] | select(.matcher=="Bash") | .hooks | length == 2' plugins/sdlc-lite/hooks/hooks.json`
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh | grep -q 'hook selftest: PASS'`
- `grep -q 'hook-selftest.sh' plugins/sdlc-lite/scripts/check.sh`
- (guard) `printf '{"tool_input":{"command":"git %s"}}' push | SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh 2>/dev/null; test $? -eq 2`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/hooks/*.sh plugins/sdlc-lite/scripts/*.sh`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (green on the base commit today)

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

## Risks
- The plan assumes the Bash PreToolUse payload carries `tool_input.run_in_background` as a JSON boolean when the model sets it. If the harness drops it or sends a string, the hook never fires. The selftest only uses fixtures, so the builder should confirm the field name against the hooks docs, or a live `claude -p` probe with `SDLC_HEADLESS=1` if that is cheap.
- The Agent tool also has `run_in_background`, and it defaults to background. A headless conductor that delegates through Agent could still abandon work. This plan matches only the Bash tool, as the ticket proposes.
- A criterion or command that contains a literal `git push` is blocked by block-publish.sh inside role runs, including the verifier's. The guard criteria build the string with `printf`, and the selftest must do the same.
- The new hook loads at session start. The builder's own session will not have it, but the verifier's will, so the verifier must run its criteria in the foreground.

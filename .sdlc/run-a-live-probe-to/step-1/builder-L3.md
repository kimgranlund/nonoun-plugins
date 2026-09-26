<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/hook-live-probe.sh`: added the `--agent` flag, which `usage`/`--help` now lists. Agent mode makes a deny run and an allow run. Each run registers three hooks through its own `--settings`: a PreToolUse capture on the Agent matcher, a PreToolUse logger on `*` that writes `tool_name` to `tools.log`, and a PostToolUse recorder on the Agent matcher. It prints the `agent deny:`, `agent allow:` and `verdict:` lines, and its `--out` report is headed `# Hook live probe (Agent)`. The capture wrapper and the claude runner became shared functions (`write_capture`, `run_claude`), and the Bash probe behaves as before. The stub claude now picks its payload from the prompt, finds hooks by matcher, and runs PostToolUse only when every PreToolUse hook exited 0. Added selftest cases (f) to (j), plus (f2), where the deny payload is `true`. The header comment is updated.
- `CLAUDE.md`: updated the "Live hook probe" command bullet (`[--agent]` in the synopsis, what `hook-live-probe.sh --agent` checks, selftest covers the Agent path) and the `hooks/block-background.sh` layout bullet.
- `.claude/agents/sdlc-lite-author.md`: the hook-live-probe sentence now covers `hook-live-probe.sh --agent` and says the selftest covers the Agent path.

## Checks
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --help 2>&1 | grep -qF -- '--agent'`: exit 0.
- Selftest with an Agent-blind hook (criterion command as written): the selftest failed at (f) with `agent deny: hook exit code 0, not 2`, so `test "$rc" -ne 0` exited 0.
- Selftest with a hook that denies `false` (criterion command as written): the selftest failed at (f) with `agent allow: hook exit code 2, not 0`, so the criterion exited 0.
- `grep -qF '"tool_name":"Task"' plugins/sdlc-lite/scripts/hook-live-probe.sh`: exit 0.
- `grep -qF 'hook-live-probe.sh --agent' CLAUDE.md`: exit 0.
- `grep -qF 'hook-live-probe.sh --agent' .claude/agents/sdlc-lite-author.md`: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: `hook live probe selftest: PASS`, rc 0.
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-live-probe.sh`: exit 0.
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/hooks.json plugins/sdlc-lite/hooks/block-background.sh`: exit 0.
- Extra, not a criterion: `python3 plugins/sdlc-lite/scripts/check.py` printed `ok: 18 role levels, 8 agents checked`.
- Extra, not a criterion: plain `shellcheck` (all severities) reports one SC2329 info about `cleanup`, which is only called from traps. The base HEAD, checked in a throwaway worktree that has since been removed, reports the same finding, so it is not new.

## Notes
- The host load average was about 90 during this run. The selftest took 4:19 here, and the base version took 1:42 on the same host. It now makes 12 more probe runs (six Agent cases, two claude runs each), so it adds time to `check.sh` under load.
- Live mode was not run in this step; that is step 2. The live claude also loads the user's installed plugins. If an installed sdlc-lite has its own Agent-matcher `block-background.sh`, that copy also sees the calls. It should agree with this hook, but if it blocked the allow call, the probe would report `no PostToolUse(Agent) record`.
- Selftest case (i) runs a copy of the script in `$st/deny-all/scripts` next to a stub hook that always exits 2. This needed no new test-only env var or flag in the script.
- `.sdlc/run-a-live-probe-to/handoff.md` was already modified before this step. I did not touch it.

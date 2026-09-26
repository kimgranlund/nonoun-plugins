<!-- role=filer level=L1 model=sonnet effort=medium -->
All three steps built and verified pass. Now composing the final filer message.

## Warnings
None

## PR title
T-0092: Add a live `--agent` probe to hook-live-probe.sh and record the confirmed result

## PR body
**Summary**

Follow-up from T-0076: confirms live, against the installed Claude Code (2.1.281), that the subagent tool reaches `PreToolUse` as `tool_name` `Agent` (so `hooks.json`'s `"matcher": "Agent"` fires), that `hooks/block-background.sh` denies an Agent call with `run_in_background` missing or `true` under `SDLC_HEADLESS=1`, and that a call with `run_in_background: false` is accepted by the tool schema and passes the hook. The recorded live result is PASS on every count.

**Changes**

- `plugins/sdlc-lite/scripts/hook-live-probe.sh`: added a `--agent` mode (listed in `--help`/`usage`) alongside the existing Bash probe. It runs a deny run and an allow run, each registering three hooks via its own `--settings`: a PreToolUse capture on the `Agent` matcher, a PreToolUse logger on `*` (names the tool actually seen if not `Agent`), and a PostToolUse recorder on `Agent`. Prints `agent deny:`, `agent allow:`, and `verdict:` lines; `--out` report is headed `# Hook live probe (Agent)`. Refactored shared `write_capture`/`run_claude` helpers; Bash probe behavior unchanged. Selftest extended offline with cases (f) through (j) plus (f2), covering an Agent-blind hook, a hook that denies `false`, a `Task`-named tool, `run_in_background` as the string `"false"`, an allow payload the hook denies, and a deny payload of `true` the hook lets through.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: updated to describe `hook-live-probe.sh --agent` and state the offline selftest covers the Agent path.
- `.sdlc/run-a-live-probe-to/agent-probe.md`: the one live run's recorded result (haiku, Claude Code 2.1.281): deny run captured `tool_name Agent`, `run_in_background` absent, hook exit code 2; allow run captured `tool_name Agent`, `run_in_background false`, hook exit code 0, PostToolUse recorded. `verdict: PASS`.

No hook or hooks.json file was touched (all three steps guard `git diff --quiet HEAD -- plugins/sdlc-lite/hooks`), per the constraint against silently changing them.

**Verification**

- Step 1 (builder L3 / verifier L2, pass): all acceptance criteria including the two selftest-bites checks and the `--agent` help/grep checks confirmed on the built tree and shown red on base HEAD (RED/GREEN discriminated); `hook-live-probe.sh --selftest` and `shellcheck --severity=warning` both green; docs greps green.
- Step 2 (builder L1 / verifier L1, pass): kept the already-produced live probe record as-is (no new model call); every guard criterion (`agent-probe.md` shape, verdict/version lines, hooks dir untouched, no new untracked files under `plugins/`) confirmed pass, with red/green fixture checks by the verifier.
- Step 3 (builder L1 / verifier L1, pass): full repo gates green — `hook-live-probe.sh --selftest`, `hook-selftest.sh`, `check.py`, and `check.sh` (foreground, ~15 min under load) — with the verifier independently reproducing each gate's failure mode in a throwaway worktree to confirm it actually discriminates.
- A plan-defect replan (planner L3) fixed a step-2 criterion that impossibly compared step 1's uncommitted probe script against HEAD, and re-split step 3 with a longer guard timeout after the default 300s guard timed out (not a red finding; `check.sh` legitimately takes 7–15 min on this host).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Added a live `--agent` mode to `hook-live-probe.sh`, confirming against the installed Claude Code that the subagent tool reaches `PreToolUse` as `Agent` and that `block-background.sh` correctly denies/allows Agent calls by `run_in_background`; offline `--selftest` now covers this path too.

## Follow-ups
None

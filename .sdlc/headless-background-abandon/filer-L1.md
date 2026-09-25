<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0072: Deny background Bash in headless sessions so role runs are not abandoned

## PR body
### Summary
Headless sessions (`claude -p`: role runs, bench, fanout lanes, dogfood launchers) sometimes started a role run or a gate with `run_in_background: true` and then ended the turn. Ending the turn ends a headless session, so the work was abandoned. In the T-0061..T-0064 dogfood batch this left a `planner-L2.log` with no `.md`. It also produced a false verifier fail in a peer repo. The docs already said to run in the foreground, and that was not enough. This PR enforces it with a PreToolUse(Bash) hook.

### Changes
- New `plugins/sdlc-lite/hooks/block-background.sh`. When `SDLC_ROLE` is set or `SDLC_HEADLESS=1`, it denies `run_in_background: true` with exit 2. Its message says to run in the foreground with the Bash timeout at 600000 or more and not to end the turn. A value of false, absent, or null passes.
- `hooks/hooks.json` registers the new hook as a second hook under the existing Bash matcher. `block-publish.sh` is unchanged.
- New `scripts/hook-selftest.sh`, wired into `check.sh`. It covers 6 block-background cases, including the negative control with neither variable set, and the block-publish push and `ls` cases. Every case runs under `env -u SDLC_ROLE -u SDLC_HEADLESS` so the caller's env cannot leak in.
- `scripts/bench.sh` and `fanout.py`'s lane driver env now set `SDLC_HEADLESS=1`. The fanout selftest stub fails if the variable is missing.
- The headless sentence in `skills/chain`, `skills/bench`, `skills/fanout`, and `agents/conductor.md` now names the hook. It also states the convention: other headless launchers must set `SDLC_HEADLESS=1` themselves. `check.py`'s long-run doc check now requires the word `SDLC_HEADLESS`.
- Repo `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` describe the hook and the convention.
- Plugin version bumped to 0.8.2.

### Verification
- Step 1 passed the verifier (L1, Sonnet medium):
  - Each exit code was checked directly: 2 for a role or headless session with background true, 0 for the negative control, 0 when background is absent or null.
  - hooks.json has 2 Bash hooks (checked with jq).
  - The hook selftest prints PASS.
  - The block-publish guard still bites.
  - shellcheck is clean and `check.sh` exits 0.
  - The verifier made the selftest go red by breaking the hook in a throwaway copy.
- Step 2 passed the verifier (L1):
  - The grep criteria passed on bench.sh, the fanout stub, the four docs, check.py, CLAUDE.md, the author agent, and plugin.json.
  - `fanout.py selftest` prints PASS.
  - `check.sh` exits 0.
  - Negative control: in a throwaway fanout.py copy without the env line, run under `env -u SDLC_HEADLESS`, the selftest went red.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: headless sessions can no longer background a Bash command. The new `hooks/block-background.sh` denies `run_in_background: true` when `SDLC_ROLE` is set or `SDLC_HEADLESS=1`, so role runs and gates are no longer abandoned. `bench.sh` and fanout lanes set `SDLC_HEADLESS=1`, and other headless launchers must set it themselves. (0.8.2, T-0072)

## Follow-ups
- Confirm with a live `claude -p` probe that the Bash PreToolUse payload carries `tool_input.run_in_background` as a JSON boolean. `block-background.sh` is proven only against fixtures, so a different field shape would silently disable it.
- Headless conductors can still abandon work through the Agent tool's `run_in_background`, which defaults to background. `block-background.sh` matches only Bash, so extend the guard to Agent in headless sessions.

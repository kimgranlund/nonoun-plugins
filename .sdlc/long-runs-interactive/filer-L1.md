<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0042: Document long role runs in interactive sessions

## PR body
### Summary
The /chain, /bench and conductor docs told agents to run every role in the foreground with a 600000 ms timeout and never use `run_in_background`. A full bench /chain takes 15 to 30 minutes. That is past the Bash tool's 10-minute cap, and an interactive session cannot raise the cap the way `scripts/bench.sh` does for headless runs. The docs now cover both cases:

- **Headless** (`claude -p`, including `bench.sh`): run roles in the foreground.
- **Interactive**: run roles in the background and wait for the completion notification. Never poll with `sleep`.

### Changes
- **Step 1: `plugins/sdlc-lite/scripts/check.py`.** Adds a check on the long-run docs, landed before the fix.
  - It covers `skills/chain/SKILL.md`, `skills/bench/SKILL.md` and `agents/conductor.md`.
  - Each file must contain the words `interactive`, `run_in_background`, `notification` and `sleep`.
  - It fails if any of those files still says `never run_in_background`, and it fails if any of them is missing.
  - The same step extended the hazard line in `.claude/agents/sdlc-lite-author.md` with the interactive rule.
- **Step 2: the three docs.** `skills/chain/SKILL.md` (intro), `skills/bench/SKILL.md` (line 11) and `agents/conductor.md` (first bullet under "How you run roles") each now state both cases:
  - **Headless:** foreground, `timeout` at 600000 or more, no `run_in_background`. Ending the turn abandons the run.
  - **Interactive:** `run_in_background: true`, wait for the completion notification, never poll with `sleep`, and read `<role>-<level>.md` once notified. Ending the turn is safe.
  - Line 26 of `.claude/agents/sdlc-lite-author.md` was updated to match.
- **CLAUDE.md is unchanged.** Its "Headless runs" bullet is about `--dangerously-skip-permissions`, not about how long runs are launched.

### Verification
- **Step 1: verifier L1 pass.**
  - Before the doc fix, `check.py` exited 1 with FAIL lines for chain, bench and conductor.
  - Deleting `conductor.md` in a throwaway copy produced `FAIL agents/conductor.md: missing`.
  - The diff touches no `.sh` files.
- **Step 2: verifier L1 pass.**
  - `check.py` exited 0 ("ok: 18 role levels, 8 agents checked").
  - `check.sh` exited 0: selftests, shellcheck and plugin validate all passed.
  - `grep -c run_in_background` counts 1 in each doc.
  - The four edited files contain no em dashes.
  - The diffs show both cases in each file.
- **Not verified:** background runs have not been tried in a live interactive session. The docs assume the harness re-invokes the session when a background run exits, and the planner flagged this as unverified. The new check only matches wording.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: /chain, /bench and the conductor now say how to run long role runs in interactive sessions. They run in the background, the session waits for the completion notification and never polls with `sleep`. Foreground runs with a raised timeout are now for headless sessions only. `check.py` enforces this wording.

## Follow-ups
- Verify with one live interactive /chain run on a throwaway repo that a `run_in_background` role run re-invokes the session on exit, as the T-0042 docs assume (the planner flagged this as unverified).

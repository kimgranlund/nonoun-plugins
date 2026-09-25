<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0061: Add `steps.py next` so /chain gets its escalation action from code

## PR body
### Summary
The /chain step 4 escalation action is now computed in code. Before this change, /chain and the conductor worked out the action from prose. A new read-only `steps.py next <step dir>` reads the newest builder and verifier results using `order.py` ordering and prints the next action. That way a `plan defect:` tag or a blocked build can no longer be routed to a rebuild by mistake.

### Changes
- **`plugins/sdlc-lite/scripts/steps.py`** (step 1, builder L3): new `next <step dir>` subcommand.
  - Output: the first line is `<action>` or `<action> L<n>`, where the action is one of `build`, `verify`, `rebuild`, `bump`, `replan`, `done`, `stop`. Then come `reason:` and `read:` lines.
  - Rules:
    - A blocked build gives `replan`.
    - A verifier fail whose next-attempt note starts with `plan defect:` gives `replan`. These fails never count toward a bump.
    - A verifier result counts only if it is newer than the newest builder result, using `order.counts_after`.
    - The verifier level follows the build level: L1/L2 → L1, L3 → L2, L4/L5 → L3.
  - It writes nothing and never reads file times.
  - Errors: one `steps next: ` line on stderr, empty stdout, exit 1. This covers a missing dir, a missing handoff or `level:` line, a bad Status, and a bad Verdict.
  - Docstring and argparse updated. 19 `next ` selftest checks added.
- **`plugins/sdlc-lite/skills/chain/SKILL.md`** section 4 (step 2, builder L2): runs `steps.py next` after each builder and verifier run and maps each action to what to do next. A nonzero exit means stop and report. The prose rules stay as the spec.
- **`plugins/sdlc-lite/agents/conductor.md`**: the escalation line now points at `steps.py next`.
- **`CLAUDE.md`**: updated the `scripts/steps.py` Layout line, the Roadmap "Escalation is enforced" sentence, and the plan-defect Decisions bullet.
- **`.claude/agents/sdlc-lite-author.md`**: `steps.py next` added to the plan-defect sync list.
- `order.py` is unchanged.

### Verification
- **Step 1: verifier L2 (Fable medium), pass.**
  - All 13 behavior criteria passed in the working tree and failed at HEAD, where `next` does not exist yet.
  - A probe of every error kind gave rc=1, empty stdout, and no files changed.
  - Mutation tests showed the selftest catches real bugs: disabling plan-defect detection, breaking the L4 verifier mapping, and making `next` write a file each turned it red.
  - The split/lint `ok:` lines match a HEAD worktree exactly (22 lines).
  - `order.py` diff is empty.
  - `check.sh` exits 0.
- **Step 2: verifier L1 (Sonnet medium), pass.**
  - All 5 grep criteria passed, and the verifier confirmed each one fails at HEAD.
  - No em dashes in the touched files.
  - `check.sh` exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `steps.py next <step dir>`. It prints the next /chain step 4 action (`build`, `verify`, `rebuild`, `bump`, `replan`, `done`, `stop`) from the newest builder and verifier results. /chain and the conductor now follow it after every builder and verifier run, so plan defects and blocked builds always go to a replan. (T-0061)

## Follow-ups
- Add a `steps.py selftest` case for a done L3 build → `verify L2`: a mutant mapping L3 to verifier L3 left the selftest green (step 1 verifier observation).

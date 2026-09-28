<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0049: Pick newest result from runs.jsonl order, not mtime

## PR body
### Summary
Some verdicts depended on file mtime to find the newest builder, verifier, planner or filer result. A git checkout gives every file the same mtime, so a fresh worktree could pick an older result. In one review, bench-summary reported button-geometry as 2/3 steps passed in a fresh worktree and 3/3 on the original checkout. With this change, every one of those decisions goes through one shared rule in `scripts/order.py`: the latest `runs.jsonl` record wins, else level, then rerun index, then name. The rule never reads mtime.

### Changes
1. **Shared ordering helper** (`scripts/order.py`, new)
   - Provides `ordered`, `newest` and `counts_after`, plus a CLI (`newest <dir> <role>`, `selftest`).
   - Records that carry `file` rank their file directly.
   - Older records without `file` pair with that role and level's files, starting from the end.
   - Files with no record sort first, by level, then k, then name.
   - `run.sh` now writes `file` on every `runs.jsonl` line, and `check.sh` runs the order selftest.
   - Verified (verifier L2, pass):
     - The selftest passes 15 checks. The grep for `mtime` and `stat()` in the module finds nothing.
     - The committed button-geometry step-2 was copied and every file touched to one time. `newest` still returns `verifier-L2.md` and `builder-L3.md`.
     - Negative control: changing the sort key to mtime made 5 checks fail.
     - Negative control: removing `file` from run.sh made the run selftest fail.
2. **board.py** reads verdicts through `order.py`:
   - `by_level` uses `order.ordered`.
   - `.running` files sort by level, then name.
   - The verifier-after-build check uses `order.counts_after`.
   - Task display order still uses mtime.
   - Verified (verifier L1, pass):
     - The selftest passes, including the new fixtures with equal mtimes and with mtimes in reverse order.
     - On the touched button-geometry copy, step 2 shows 🟢 pass · builder L3 · verifier L2.
     - Negative control: reverting to the mtime comparison failed 2 cases.
3. **steps.py and tickets.py** pick the newest planner and filer through `order.py`. Selftests (c) and (h) are rewritten with equal mtimes, reverse mtimes, and no-record fallbacks.
   - Verified (verifier L1, pass): both selftests pass. Restoring the mtime key failed all six rewritten cases.
4. **run.sh and bench-summary.sh**
   - The verifier model swap and bench-summary's verifier pick now call `order.py newest`.
   - `run-selftest.sh` gains dry-run swap cases where both builder files have the same mtime.
   - Verified (verifier L1, pass):
     - The run selftest passes. Reverting to `ls -t` made it fail.
     - bench-summary reports 3 of 3 on the touched button-geometry copy.
     - The grep for `ls -t` and `-nt` finds nothing.
     - shellcheck is clean.
5. **Docs**
   - `handoff-format/SKILL.md`, `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` now state the runs.jsonl rule.
   - Comments in steps.py and tickets.py that said "by mtime" were reworded.
   - Verified (verifier L1, pass):
     - The only "by mtime" text left is task display order in board.py.
     - `order.py` is mentioned in all three docs.
     - `check.sh` exits 0.
     - Plugin validate shows one warning, about the unquoted `${CLAUDE_PLUGIN_ROOT}` in hooks. It was already present before this change. It is not the CLAUDE.md warning the handoff expected.

### Known limits (from the plan)
- For `runs.jsonl` trails written before this change, matching records to files is a guess. It may point to the wrong file where runs were deleted or files were renamed by hand.
- A file with no record never counts as newest next to files that have one.
- `counts_after` is true when either file has no record.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: the newest builder, verifier, planner and filer result is now picked from the recorded run order in `runs.jsonl` (via the new `scripts/order.py`), never from file mtime. A fresh clone or checkout now reads the same verdicts as the machine that ran them. `runs.jsonl` lines now record the result `file`.

## Follow-ups
- order.py crashes with IndexError when run with no arguments (while printing its usage from `__doc__`) instead of printing usage and exiting cleanly.
- order.counts_after returns true when either file has no runs.jsonl record, so a stale unrecorded verifier can still show pass over a newer recorded build on the board.
- The hooks.PreToolUse command leaves `${CLAUDE_PLUGIN_ROOT}` unquoted, which `claude plugin validate` warns about. A plugin path with spaces could break the block-publish hook.

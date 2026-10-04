<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/supervisor.py`:
  - `wake_prompt` now includes the Claude Code Bash sentence.
  - The `Prompt (D4):` line in the docstring mentions that sentence.
  - New constants `ST_BASH_SENTENCE` and `BASH_RULE`.
  - `st_prompt` returns the new text.
  - New patch `CTL_OLD_PROMPT`, new case `case_prompt_bash`, and two new `SELFTEST_CASES` entries placed after the topic-leaking control.
- `docs/ticket-stages/watcher-design.md`: in "The wake prompt", replaced the `- Text:` line with the new prompt and added the item about the first live run after it.

## Checks
- AC1, the supervisor selftest with the folder-unchanged checks and the required `ok:` lines: `supervisor selftest: PASS`, all 5 lines present, exit 0.
- AC2, the `python3 -c` assertions on `wake_prompt("bob", 2)`: exit 0.
- AC3, the greps on `watcher-design.md`: exit 0.
- Guard, the diff and untracked-file whitelist with `SDLC_BASE_SHA` taken from the env or `step-5/base-sha`: exit 0.
- `git diff --check`: clean.
- Em-dash grep on both files: 0 matches.
- `if __name__ == '__main__':` appears exactly once in `supervisor.py`.

## Notes
None

<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/check.py`: new long-run doc check, placed before the final error print. It covers `skills/chain/SKILL.md`, `skills/bench/SKILL.md` and `agents/conductor.md`. A missing file fails. It is a plain string test on each file's text for `interactive`, `run_in_background`, `notification` and `sleep`, and it fails on any `never run_in_background` (with or without backticks).
- `.claude/agents/sdlc-lite-author.md`: extended the headless-foreground hazard line with the same rule for interactive sessions and a note that `check.py` enforces it.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 1, as required before Step 2. It printed FAIL lines for chain (missing words, plus the unqualified never-background text), bench (same two) and conductor (all four words missing).
- `shellcheck scripts/*.sh`: two info-level notes (SC2012, SC2016), both in `run.sh`, which this step did not touch. Each note's code line matches `run.sh` as it stands, so they predate this change.
- `tickets.py selftest`, `steps.py selftest`, `board.py selftest`: all exit 0.
- I did not run `scripts/check.sh` as a whole. It includes `check.py`, which is meant to fail until Step 2.

## Notes
- For Step 2: the unqualified-phrase test matches the literal text `never run_in_background` (and the backticked form) anywhere in the file. The fixed docs must not contain that phrase at all, even in a sentence that limits it to headless sessions. Word it another way, for example "keep it in the foreground (headless only)".

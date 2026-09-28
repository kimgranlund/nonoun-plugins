<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: added `--sort {recent,id,name}` (default `recent`), a `sort_tasks()` helper, and changed `main()` so it sorts first and then applies the `belongs_on_board` filter. Added `os` to the imports. Added selftest case 6.
- `plugins/sdlc-lite/skills/board/SKILL.md`: added `[--sort {recent,id,name}]` to `argument-hint`. Step 2 now passes `--sort <mode>` through.

## Checks
- 🟢 `python3 plugins/sdlc-lite/scripts/board.py selftest`: `board selftest: PASS`.
- 🟢 Negative control: I inverted the id sort key and the selftest failed on the `--sort id` case (`got ['zulu-three', 'yankee-two', 'alpha', 'bravo']`). After I restored the key it passed again.
- 🟢 `plugins/sdlc-lite/scripts/check.sh`: every section ok (role levels, selftest, tickets and board selftests, shellcheck, plugin validate).

## Notes
- The handoff says to run `scripts/check.sh`, but that script is at `plugins/sdlc-lite/scripts/check.sh`. There is no repo-root `scripts/` directory.
- I did not run the manual criteria as separate commands. Selftest case 6 covers them by calling `main()` as a subprocess on fixtures with set mtimes. The `T-0003` dir is older than the `T-0002` dir there, the reverse of the handoff's wording, but `--sort id` ignores mtime, so it proves the same thing. The case checks:
  - `--sort id`: `T-0002` before `T-0003`, then the two tasks without tickets, alphabetically.
  - `--sort name`: strict alphabetical order.
  - No flag: mtime order.
  - No flag and `--sort recent`: identical output.
- The equality check deletes `.board-state.json` before each of those two runs. Otherwise the ` · changed` markers written by one run would make the next run's output differ.
- For `--sort id`, a task whose front matter id has no `T-<digits>` part is treated like a task with no ticket.

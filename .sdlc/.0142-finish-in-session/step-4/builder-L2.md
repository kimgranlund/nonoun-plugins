<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/fix/SKILL.md`: new `/fix` fast-lane skill. It has the frontmatter, the long-run rule, and 5 steps: size gate, handoff with `steps.py lint`, build and verify with one rebuild, close with `--reason`, and publish only after approval, then report with the board.
- `plugins/sdlc-lite/agents/conductor.md`: new Route bullet sending size S to `/sdlc-lite:fix`, "the fast lane with no planner, filer, or follow-up tickets". The trivial-edits section is unchanged.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: new paragraph under the Loose ends step. The `/fix` fast lane runs builder L1 or L2 and verifier L1, with one rebuild and no bump; a second fail goes to /chain.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the by-hand sentence now also names `/fix` and its `step-1/`.
- `plugins/sdlc-lite/scripts/check.py`: `skills/fix/SKILL.md` added to the long-run docs tuple. `sdlc-lite:fix` (conductor) and `fast lane` (fix skill, conductor, level-rubric) added to `FINISH_DOCS`. `finish_missing` now requires that no word character or `-` follows the matched word.
- `CLAUDE.md` (repo root): `/fix` added to the Launcher skills list with a short description.

## Checks
- The 11 `test -f` and `grep` criteria: all passed.
- Negative control with `run_in_background` renamed to `rib` in fix/SKILL.md: check.py flagged `skills/fix/SKILL.md ... run_in_background` (grep exit 0).
- Negative control with `sdlc-lite:fix` renamed to `sdlc-lite:fixx` in conductor.md: check.py flagged `agents/conductor.md ... sdlc-lite:fix` (grep exit 0).
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 18 role levels, 8 agents checked`, exit 0.

## Notes
- **Why `finish_missing` changed:** the `fixx` negative control cannot fail with a plain substring check, because `sdlc-lite:fixx` still contains `sdlc-lite:fix`. I changed `finish_missing` to a regex that requires no word character or `-` after the word, so that criterion can be flagged. The existing `FINISH_DOCS` words (`fix-now:`, `decide:`, `notes.md`, `Loose ends`) still pass on the real tree.
- The full `check.sh` was not run; the handoff leaves it for the final step.

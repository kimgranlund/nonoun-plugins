<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/chain/SKILL.md`: added `## 5. Loose ends` (four numbered items covering the draft filer run, what to collect, a hand-written and linted `step-<n+1>/handoff.md`, and one build and verify with a single report line and no escalation). Renumbered File to `## 6. File` (the /file flow through 3.2, with `filer-L1-2.md` or the reused draft) and Close out to `## 7. Close out` (one AskUserQuestion call with the decide question, the publish question and up to two open items; the unattended path has no call). The frontmatter description now names the loose ends and close-out round.
- `plugins/sdlc-lite/skills/open-questions/SKILL.md`: Collect now includes the newest filer's `decide:` follow-ups when /file has not asked them yet. Ask once now says the /file decide and publish questions take two of the four slots under /chain 7.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the Layout tree has a `.sdlc/notes.md` line. In the step handoff section, "no one writes them by hand" is replaced with /chain 5 writing the `Loose ends` step by hand and linting it with `steps.py lint`; `steps.py swap` is still named as the one other writer. The merge-step block is unchanged.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: new prose subsection `### Loose ends step` after the builder paragraph, with no table rows.
- `plugins/sdlc-lite/agents/conductor.md`: one bullet under How you run roles on routing `fix-now:`, `decide:` and `note:` follow-ups.
- `plugins/sdlc-lite/scripts/check.py`: `FINISH_DOCS` extended as specified, with a new `Loose ends` key over 5 files. Docstring item 9 updated to match.
- `CLAUDE.md`: the `/chain` entry in the Layout skills bullet now names the Loose ends step and the one close-out round.

## Checks
- All 12 grep criteria: PASS.
- Negative-control criterion (copy the tree, change "Loose ends" to "Loose threads" in the chain skill, run check.py): PASS. The output holds `FAIL skills/chain/SKILL.md: finish-in-session wording missing "Loose ends"`.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 18 role levels, 8 agents checked`, rc=0. It was also green before my edits.
- `steps.py lint` on a step handoff file: `steps lint: ok` on this step's handoff. A hand-made step file with an unparseable criterion was refused (rc=1, `plan defect:`). So the lint command that /chain 5 prescribes does work on a single step handoff.

## Notes
- Steps 1 and 2 were already in the tree as uncommitted edits to `tickets.py`, `filer.md`, the file, ticket and fanout skills, `check.py` and `CLAUDE.md`. My edits sit on top of them, and nothing was committed.
- A grep for other citations of the old `/chain 5` and `/chain 6` numbers found none, including in `.claude/agents/sdlc-lite-author.md`.
- The full `scripts/check.sh` was not run; the handoff leaves it for the final step.

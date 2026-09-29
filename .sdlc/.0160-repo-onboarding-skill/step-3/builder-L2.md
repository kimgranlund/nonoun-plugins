<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/onboard/SKILL.md (new): the onboard skill. It has frontmatter, the Codex host line, the three commands, the check labels, a four-step workflow and rules.
- plugins/sdlc-lite/skills/sdlc-lite/SKILL.md: added the route table row "Set up or check entry files and docs layout | onboard".
- plugins/sdlc-lite/scripts/check.sh: added the onboard.py selftest line after fanout and named it in the header comment.
- plugins/progressive-context/skills/progressive-context/references/sdlc-lite.md: added one sentence naming SDLC Lite's `onboard` skill as the setup step. It has no path link.
- docs/repo-onboarding/design.md: the status line now says T-0160 implements the design in onboard.py and the `onboard` skill.
- docs/repo-onboarding/README.md: now says "The design is implemented; the reorganization is not."

## Checks
- Ran all 8 acceptance criteria as written: all passed.
- `python3 scripts/check-packaging.py`: PASS (catalog parity, identity, skill routes, hook isolation and context links).
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: all gates reported positive ok and negative ok.
- `git diff --check`: clean.
- Did not run the full `check.sh`.

## Notes
- The labels listed in the skill come from `LABELS` in onboard.py, plus the `present` label that `run_check` uses for docs/layout.md.
- The design.md status line still begins "proposed v0.7". The handoff asked only to replace the "Nothing implemented" sentence, so I left the rest of the line as it was.

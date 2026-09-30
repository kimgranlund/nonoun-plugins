<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `head -5 .../onboard/SKILL.md | grep -qx "name: onboard"`: pass. Evidence: I ran it and it exited 0. SKILL.md line 2 is `name: onboard`.
- `grep -qF "../sdlc-lite/SKILL.md" .../onboard/SKILL.md`: pass. Evidence: exit 0. The Codex host line links `../sdlc-lite/SKILL.md`.
- The `for w in ...` loop over the three required strings: pass. Evidence: it printed no `miss` lines. The strings are the setup dry-run command, `onboard.py check`, and the allowed-tools line. I read the file and all three are present.
- The route-table row in `skills/sdlc-lite/SKILL.md`: pass. Evidence: exit 0. The diff adds `| Set up or check entry files and docs layout | onboard |`.
- The selftest line in `check.sh`: pass. Evidence: exit 0. The diff adds the line and names it in the header comment.
- The progressive-context reference names `onboard` and has no path link to it: pass. Evidence: exit 0. The diff shows one added sentence with no link.
- Design.md no longer says "Nothing in this document is implemented": pass. Evidence: exit 0. The diff replaces it with a statement about `onboard.py` and the `onboard` skill.
- README.md no longer says "Nothing here is implemented": pass. Evidence: exit 0. The diff replaces it with "The design is implemented; the reorganization is not."
- Bite check: each new-behavior check goes red before the change. The `onboard` skill directory is untracked, so criteria 1 to 3 have nothing to match at the base commit. Criteria 7 and 8 test for strings that the diff shows being removed. Criteria 4 to 6 test for lines the diff adds. Criterion 6 also has a negative half that rejects a path link.
- Extra checks: `python3 scripts/check-packaging.py` printed PASS. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` ended with the gate lines `positive ok, negative ok`. `git diff --check` was clean.

## Out of scope changes
None. The changed files are the two docs, the reference, `check.sh`, the route SKILL.md, and the new `onboard/` skill directory. The `.sdlc` step artifacts are run outputs, so I dismissed them.

## For the next attempt
None

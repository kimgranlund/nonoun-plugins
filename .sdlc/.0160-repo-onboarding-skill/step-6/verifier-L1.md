<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, `setup` in a temp repo with a tracked `docs/README.md`, then `grep -qxF -- "- [README.md](README.md)" docs/AGENTS.md`: pass. Evidence: on the built tree, setup exited 0, the grep exited 0, and the generated `docs/AGENTS.md` shows `- [README.md](README.md)` first under `## Contents`. The same command at `$SDLC_BASE_SHA` gave grep exit 1, so the check goes red without the change. A repo with an empty `docs/` and no `README.md` produced `## Contents` followed by a blank line and the end marker, with no extra line.
- Criterion 2, `! grep -qF "T-0161" plugins/sdlc-lite/skills/onboard/SKILL.md`: pass. Evidence: exit 0, and the diff shows "(T-0161)" removed from the description.
- Criterion 3, `grep -qF "Status: implemented v0.7." docs/repo-onboarding/design.md`: pass. Evidence: exit 0, and the diff shows the change on line 3.
- Criterion 4, `grep -qF "<a link to README.md when it exists>" docs/repo-onboarding/design.md`: pass. Evidence: exit 0, and the diff shows the placeholder as the first line under `## Contents`.
- Criterion 5 (guard), `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: pass. Evidence: exit 0, with every gate reporting "positive ok, negative ok". The diff shows `RICH_DOCS` gaining `docs/README.md` and `RICH_CONTENTS` expecting the link, so the selftest asserts it.
- `TEMPLATE_VERSION = 1`: pass. Evidence: the generated block header reads `v1`.
- Design and script template text match: pass. Evidence: the diff adds the identical `<a link to README.md when it exists>` line in both files.

## Out of scope changes
None. The changes are `design.md`, `onboard.py` and `SKILL.md`, plus the run bookkeeping `runs.jsonl`, the filer artifacts and the `step-6/` artifacts.

## For the next attempt
None

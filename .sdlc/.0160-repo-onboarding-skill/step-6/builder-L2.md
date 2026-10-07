<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/onboard.py`: the `docs/AGENTS.md` template now has the `<a link to README.md when it exists>` line first under `## Contents`, using the same text as the design. That line becomes `- [README.md](README.md)` when `docs/README.md` exists and is dropped completely when it does not. `Model` has a new `readme` field. The selftest's rich fixture now includes `docs/README.md`, and `RICH_CONTENTS` expects the link. `TEMPLATE_VERSION` stays 1.
- `docs/specs/repo-onboarding/design.md`: added the README link placeholder under `## Contents` in the `docs/AGENTS.md` template, and changed the status to "Status: implemented v0.7.".
- `plugins/sdlc-lite/skills/onboard/SKILL.md`: removed "(T-0161)" from the description.

## Checks
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: exit 0, and every gate reported "positive ok, negative ok".
- Criterion 1 (`setup` in a temp repo with a tracked `docs/README.md`, then `grep -qxF -- "- [README.md](README.md)" docs/AGENTS.md`): exit 0.
- `! grep -qF "T-0161" plugins/sdlc-lite/skills/onboard/SKILL.md`: exit 0.
- `grep -qF "Status: implemented v0.7." docs/specs/repo-onboarding/design.md`: exit 0.
- `grep -qF "<a link to README.md when it exists>" docs/specs/repo-onboarding/design.md`: exit 0.
- `git diff --check`: clean.

## Notes
The selftest's empty fixture still checks that the `docs/AGENTS.md` block ends with `## Contents\n\n`. That confirms no line, blank or otherwise, is added when `docs/README.md` is missing.

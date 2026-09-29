## Task goal
Ship the `onboard` skill and its script `plugins/sdlc-lite/scripts/onboard.py` as specified in `docs/repo-onboarding/design.md` v0.7, with a selftest that proves every new gate and a live run on Claude Code and on Codex.

## Step 6: Loose ends
level: L2

### Do
1. `docs/AGENTS.md` links an existing `docs/README.md`. The design's Decisions table says an existing `README.md` index is kept and the entry file links to it, but the `docs/AGENTS.md` template has no slot for it. In `docs/repo-onboarding/design.md`, Templates, `docs/AGENTS.md`: add the line `<a link to README.md when it exists>` as the first line under `## Contents`. Mirror it byte for byte in the template text in `plugins/sdlc-lite/scripts/onboard.py`, fill it with `- [README.md](README.md)` when `docs/README.md` exists and with nothing (no blank line) when it does not, and extend the existing selftest fixture or gate that already covers `docs/AGENTS.md` contents so it asserts the link. Keep `TEMPLATE_VERSION = 1`, since nothing has shipped.
2. In `plugins/sdlc-lite/skills/onboard/SKILL.md` frontmatter, remove the ticket reference "(T-0161)" from the description. Consumers cannot see this repository's tickets.
3. In `docs/repo-onboarding/design.md` line 3, change "Status: proposed v0.7." to "Status: implemented v0.7.".

### Acceptance criteria
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && mkdir docs && printf "# Docs\n" > docs/README.md && git add docs/README.md && python3 "$s" setup && grep -qxF -- "- [README.md](README.md)" docs/AGENTS.md`
- `! grep -qF "T-0161" plugins/sdlc-lite/skills/onboard/SKILL.md`
- `grep -qF "Status: implemented v0.7." docs/repo-onboarding/design.md`
- `grep -qF "<a link to README.md when it exists>" docs/repo-onboarding/design.md`
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`

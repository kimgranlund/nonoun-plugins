## Task goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout, without losing anything it already wrote.

## Step 3: Onboard skill, wiring, and records
level: L2
### Do
- Create `plugins/sdlc-lite/skills/onboard/SKILL.md`, using `plugins/sdlc-lite/skills/ticket/SKILL.md` as the pattern.
  - Frontmatter: `name: onboard`; a description saying it sets up or checks the entry files and docs layout for a repository adopting SDLC Lite and is NOT for moving existing documents (T-0161); and `allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py:*)`.
  - The body starts with the Codex host line the other skills carry. It must contain `../sdlc-lite/SKILL.md`, which `scripts/check-packaging.py` requires.
  - Workflow: run `onboard.py setup --dry-run`, show the diff, ask the user once, then run `onboard.py setup`.
  - `onboard.py check` reports the state of each file and writes nothing.
  - Name the three commands and the check labels.
  - On a parse error, report the file and line and stop.
  - The model writes no file text itself.
- Add an `onboard` row to the route table in `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`, for example "Set up or check entry files and docs layout | onboard".
- Add `python3 "$root/scripts/onboard.py" selftest || fail=1` to `plugins/sdlc-lite/scripts/check.sh` next to the other selftests, and name it in the header comment.
- Add one sentence to `plugins/progressive-context/skills/progressive-context/references/sdlc-lite.md` that names SDLC Lite's `onboard` skill as the setup step for entry files and the docs layout. Do not link to it by path, and keep the file domain-neutral.
- Update the stale records:
  - In `docs/repo-onboarding/design.md`, replace "Nothing in this document is implemented." with a statement that T-0160 implements it in `plugins/sdlc-lite/scripts/onboard.py` and the `onboard` skill.
  - In `docs/repo-onboarding/README.md`, replace "Nothing here is implemented." with a statement that the design is implemented and the reorganization is not.
### Acceptance criteria
- `head -5 plugins/sdlc-lite/skills/onboard/SKILL.md | grep -qx "name: onboard"`
- `grep -qF "../sdlc-lite/SKILL.md" plugins/sdlc-lite/skills/onboard/SKILL.md`
- `for w in "onboard.py setup --dry-run" "onboard.py check" "allowed-tools: Bash(python3 \${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py:*)"; do grep -qF "$w" plugins/sdlc-lite/skills/onboard/SKILL.md || exit 1; done`
- `grep -qE "^\|.*\| *onboard *\|$" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -qF 'python3 "$root/scripts/onboard.py" selftest || fail=1' plugins/sdlc-lite/scripts/check.sh`
- `f=plugins/progressive-context/skills/progressive-context/references/sdlc-lite.md; grep -qF "onboard" "$f" && ! grep -qE "\]\([^)]*onboard" "$f"`
- `! grep -qF "Nothing in this document is implemented" docs/repo-onboarding/design.md`
- `! grep -qF "Nothing here is implemented" docs/repo-onboarding/README.md`

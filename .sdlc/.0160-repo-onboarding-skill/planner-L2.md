<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Ship the `onboard` skill and its script `plugins/sdlc-lite/scripts/onboard.py` as specified in `docs/repo-onboarding/design.md` v0.7, with a selftest that proves every new gate and a live run on Claude Code and on Codex.

## Step 1: Layout parser and import scanner in onboard.py
level: L3
### Do
Create `plugins/sdlc-lite/scripts/onboard.py`. Use the standard library only, and keep it runnable on Python 3.9: no `match` statements and no `X | Y` type unions.

- `parse_layout(path)`: implements the "Layout file" grammar from the design.
  - The file has two sections, `## Homes` and `## Frozen paths`.
  - Inside a section, a list line is a line whose first non-space character is `-`, `*`, or `+`. It must match exactly one form:
    - A home: a backticked path ending in `/`, optionally followed by `takes` and a comma-separated list of backticked globs.
    - A frozen path: one backticked glob.
  - Lines that are not list lines are ignored.
  - Raise a `LayoutError` that carries the file path and the 1-based line number when a section heading is missing, a heading appears twice, a list line fits no form, or a home is listed twice.
  - An empty section is valid.
  - Returns the homes (with their globs) and the frozen patterns.
- `frozen_match(pattern, relpath)`: matches a path relative to the repository root.
  - A pattern ending in `/` matches everything under that folder.
  - `*` matches within one path segment, and `**` matches across segments.
- `scan_lines(text)`: yields each line with a flag that says whether the line is inside a fenced code block (``` or ~~~ fences).
- `has_import(text)`: true when a line outside any fence, with trailing whitespace removed, is exactly `@AGENTS.md` or `@./AGENTS.md`.
- Command line: argparse with the subcommands `setup`, `check`, and `selftest`. Until Step 2, `setup` and `check` may print "not implemented" and exit 2.
- How the selftest works:
  - It is built from gates. Each gate is a function that takes the implementation under test. It runs once on the real implementation, which must pass, and once on the defective variant the design names, which must fail.
  - A gate prints `gate <name>: positive ok, negative ok` only when both hold.
  - A gate that does not hold prints `gate <name>: FAIL ...`, and the selftest exits 1.
  - Fixtures live in `tempfile` directories and are removed afterwards.
- Gates in this step:
  - `layout-parsing`: a valid file parses into the expected homes and frozen patterns. A list line without backticks, a duplicate heading, and a home listed twice each raise an error with the right line number.
  - `import-detection`: `@AGENTS.md` and `@./AGENTS.md` count as the import, and an import inside a code fence does not. The negative control is a variant of `has_import` that skips the fence rule, and the gate must reject it.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qF "gate layout-parsing: positive ok, negative ok"`
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qF "gate import-detection: positive ok, negative ok"`

## Step 2: Templates, upsert table, setup and check commands
level: L4
### Do
Extend `plugins/sdlc-lite/scripts/onboard.py` so it implements these sections of the design exactly: Files, Definitions, Rules, Commands, Upsert behavior, and Templates. Read the design itself, not a summary of it.

- Templates:
  - Copy the texts byte for byte from the design's Templates section: the root `AGENTS.md`; `CLAUDE.md` for the root, `docs/`, and each topic; `docs/AGENTS.md`; `docs/layout.md`; and `docs/<topic>/AGENTS.md`. Include the role routing bullet in the root block.
  - `TEMPLATE_VERSION = 1` is one constant for the whole template set.
  - The start marker is `<!-- sdlc-lite:managed:start v<N> sha256:<H> -->` and the end marker is `<!-- sdlc-lite:managed:end -->`.
  - `<H>` is the first 12 hex characters of the SHA-256 of the block text between the marker lines, with line endings normalized to LF.
- File set:
  - The repository root is the output of `git rev-parse --show-toplevel` run from the working directory.
  - Outside a Git work tree, setup and check print a message containing "not a Git work tree" to stderr, exit 1, and write nothing.
  - Documents are the tracked Markdown files from `git ls-files`, minus `AGENTS.md`, `CLAUDE.md`, `README.md`, and `docs/layout.md`.
  - Homes come from `docs/layout.md` when it exists, and from the default layout otherwise.
  - Follow the Definitions list for topics, loose documents, the two-document threshold for a topic entry, linking the README first, excluding frozen paths, never deleting a file, and never creating an empty folder.
  - On a `LayoutError`, both commands print `docs/layout.md:<line>: <reason>` to stderr, exit nonzero, and write nothing.
- Upsert:
  - One decision function implements rows 1 to 8, and the first matching row wins.
  - A marker counts only as a whole line outside any code fence.
  - `docs/layout.md` is created when it is missing and never touched otherwise.
  - `setup --dry-run` prints a unified diff of every change to stdout and nothing else, so it prints nothing when there is no change. It writes nothing.
  - `setup` writes the same changes. `--force` replaces a block edited by hand (row 4).
  - Bytes outside the markers stay identical.
  - Rows 2, 3, and 4 are reported on stderr.
  - Size targets (60 lines for the root entry, 30 for a nested one) are reported and never trimmed.
- `check`:
  - Writes nothing.
  - Prints one line per file in the form `<label> <path>`. The labels are current, stale, edited, newer, malformed, missing, and unmanaged. For `docs/layout.md` the label is present or missing.
  - Exits nonzero when any file is not current or present.
- New selftest gates, built the same way as in Step 1 and printing `gate <name>: positive ok, negative ok`. Keep the Step 1 gates.

| Gate | Positive case | Negative control |
| --- | --- | --- |
| `create` | An empty fixture gets every applicable file, with its block and starter text. | A fixture where `docs/` is a regular file makes the run exit nonzero and leaves the fixture unchanged. |
| `preserve` | A file with user content gains a block, and the bytes outside the markers are identical. | A template variant that writes outside the markers is rejected. |
| `idempotence` | A second run produces no diff. | A template variant that embeds a run counter is rejected. |
| `row-order` | One fixture per row produces that row's action. | A decision variant with rows 4 and 6 swapped is rejected. |
| `malformed-markers` | A well-formed block is replaced. | A start marker with no end marker leaves the file byte-identical and is reported. |
| `check-mode` | A current fixture exits zero. | A stale, an edited, a missing, and an unmanaged fixture each exit nonzero with the matching label. |
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- `out=$(python3 plugins/sdlc-lite/scripts/onboard.py selftest) && for g in layout-parsing import-detection create preserve idempotence row-order malformed-markers check-mode; do printf "%s\n" "$out" | grep -qxF "gate $g: positive ok, negative ok" || exit 1; done`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && python3 "$s" setup && for f in AGENTS.md CLAUDE.md docs/AGENTS.md docs/CLAUDE.md docs/layout.md; do test -f "$f" || exit 1; done`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && python3 "$s" setup && python3 "$s" check && test -z "$(python3 "$s" setup --dry-run)"`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && python3 "$s" setup && grep -qF "Do not spawn another plugin's builder, planner, or reviewer agent in their place." AGENTS.md && grep -qxF "@AGENTS.md" CLAUDE.md && grep -qE "^<!-- sdlc-lite:managed:start v[0-9]+ sha256:[0-9a-f]{12} -->$" AGENTS.md`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && printf "# Mine\n\nkeep me\n" > AGENTS.md && cp AGENTS.md before.md && python3 "$s" setup && head -c "$(wc -c < before.md)" AGENTS.md | cmp -s - before.md`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && python3 "$s" setup && printf "# mine\n" > CLAUDE.md && out=$(python3 "$s" check 2>&1); rc=$?; test "$rc" -ne 0 && printf "%s\n" "$out" | grep -q "unmanaged"`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && out=$(python3 "$s" setup 2>&1); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -qF "not a Git work tree" && test -z "$(ls -A)"`
- `s="$PWD/plugins/sdlc-lite/scripts/onboard.py"; d=$(mktemp -d) && cd "$d" && git init -q && mkdir docs && printf "# Layout\n\n## Homes\n- maintenance/\n\n## Frozen paths\n" > docs/layout.md && out=$(python3 "$s" setup 2>&1); rc=$?; test "$rc" -ne 0 && printf "%s\n" "$out" | grep -qF "docs/layout.md:4" && test ! -e AGENTS.md`

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

## Step 4: Live run on Claude Code and Codex
level: L3
### Do
Run the design's live run gate in throwaway Git repositories in a temp directory outside this repository. Never commit transcripts.

For each host:
1. Run `git init` to create a project.
2. In it, run `python3 <repo>/plugins/sdlc-lite/scripts/onboard.py setup`.
3. Start a session at the project root with tools disabled.
4. Ask it to quote the line that begins "Managed by SDLC Lite onboard" if that line is in its context, and to answer ABSENT otherwise.

Host settings:
- Claude Code: headless `claude -p` with tools disabled.
- Codex: `codex exec` with a read-only sandbox, running no command, and `-m gpt-6-astra`. The default models are rejected on this account (T-0163).

Negative control: the same project with the root managed block deleted from `AGENTS.md` must not report the line.

Record the results in a new dated report, `docs/validation/onboard-live-run.md`. Include the date, host versions, models, the exact commands and prompt, and one trial per arm. Add this table with one row per arm, writing "reported" or "not reported" for what was actually observed:

| Host | Arm | Result |
| --- | --- | --- |
| Claude Code | managed block present | reported |
| Claude Code | managed block deleted | not reported |
| Codex | managed block present | reported |
| Codex | managed block deleted | not reported |

If an arm does not match the expected result, record what was observed truthfully and report Status blocked. Link the report from the Evidence list in `docs/repo-onboarding/README.md`, and from `docs/README.md` next to the other onboarding validation entries.
### Acceptance criteria
- `f=docs/validation/onboard-live-run.md; for r in "| Claude Code | managed block present | reported |" "| Claude Code | managed block deleted | not reported |" "| Codex | managed block present | reported |" "| Codex | managed block deleted | not reported |"; do grep -qF "$r" "$f" || exit 1; done`
- `grep -qF "gpt-6-astra" docs/validation/onboard-live-run.md`
- `grep -qF "../validation/onboard-live-run.md" docs/repo-onboarding/README.md`
- `grep -qF "validation/onboard-live-run.md" docs/README.md`

## Step 5: Gates green
level: L2
### Do
Run every gate below and fix any red that the earlier steps introduced, in the files those steps own. A gate that was already red at the build-start HEAD is reported as Status `inherited red`. Also run any available skill validator on `plugins/sdlc-lite/skills/onboard` and on the Progressive Context skill, and report the validation as unverified when no validator is installed.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`

## Risks
- No skill validator (`quick_validate.py` or the cross-harness validator) is installed on this host, so skill validation may end up reported as unverified.
- The live run spends model calls and depends on account access. If `gpt-6-astra` is rejected, Step 4 blocks.
- The open question of whether an installed plugin can read its own template version is not resolved here. `TEMPLATE_VERSION` is a constant in the script.
- The plugin version in the manifests is not bumped. The release decision stays with the user.

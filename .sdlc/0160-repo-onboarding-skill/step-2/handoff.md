## Task goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout, without losing anything it already wrote.

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

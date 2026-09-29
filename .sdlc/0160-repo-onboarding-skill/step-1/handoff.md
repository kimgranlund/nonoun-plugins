## Task goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout, without losing anything it already wrote.

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

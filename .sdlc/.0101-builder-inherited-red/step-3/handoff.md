## Task goal
A gate that main already made red is reported as inherited, not as a build failure or a plan defect.

## Step 3: board.py renders an inherited red step as 🔴
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- In `step_row`, right after the `blocked` check on the newest builder, add a check: when `section(last_build, 'Status')` starts with `inherited red`, return `('🔴', f'inherited red · builder {level_of(last_build)}, ask the user{tries}', LADDER['building'])`. `--summary` then counts it in `🔴<n>` without further change.
- Mention the inherited red rendering in the module docstring's Status paragraph.
- Add a selftest case in section 7, using `step_fixture`: a single builder whose result is `## Status\ninherited red: test_a\n` renders glyph 🔴 with a status that starts with `inherited red`. Its expect label must contain `inherited red`.
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Status\ninherited red: test_a\n' > "$d/builder-L2.md" && python3 -c 'import sys, pathlib; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import board; g, s, _ = board.step_row(pathlib.Path(sys.argv[1]), "x", "L2"); sys.exit(0 if g == "🔴" and s.startswith("inherited red") else 1)' "$d"` (run from the repo root)
- `grep -q 'inherited red' plugins/sdlc-lite/scripts/board.py`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`

## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 4: Result reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/results.py`: `read(dir)` returns one record per `<role>-L*.md` file in `dir`: name (without `.md`), role, level (from the name), model and effort from the first-line `<!-- role=... model=... effort=... -->` header (None when absent), `status` = `steps.build_status_or_none(path)` for a builder, `verdict` = `steps.verdict_or_none(path)` for a verifier, `plan_defect` = `steps.is_plan_defect(path)`, `swap` = `steps.swap_pair(path) is not None`, `next_note` = the first non-blank line under the For the next attempt section (a verifier) or the Notes section (a builder), `changes` = the code-span texts under the Changes section. Every section read goes through `steps.section(path, '<heading name>')` with the bare heading name; the file's text never holds the strings `## Status` or `## Verdict`, not even in a comment, so it cannot grow its own parsing of them. Register the `results` cases: builder done, blocked, `inherited red: x`, and statusless fixtures give done, blocked, inherited, and None; verifier pass, fail, and no-verdict fixtures give pass, fail, and None; a fail whose For the next attempt starts `plan defect:` gives plan_defect True; and on the same fixtures laid out as step dirs, `steps.next_action` derives the matching action (rebuild for statusless, reverify for no verdict, replan for blocked and plan defect, inherited for inherited red), so the reader classifies exactly as `steps.py next` does.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k results`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k results | grep -q '^ok: results: '`
- `grep -q 'build_status_or_none' plugins/sdlc-lite/scripts/traces/sources/results.py && grep -q 'verdict_or_none' plugins/sdlc-lite/scripts/traces/sources/results.py && grep -q 'is_plan_defect' plugins/sdlc-lite/scripts/traces/sources/results.py && ! grep -qE "## (Status|Verdict)" plugins/sdlc-lite/scripts/traces/sources/results.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

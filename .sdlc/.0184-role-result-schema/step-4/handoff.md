## Task goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Step 4: check.py guards agent bodies against the schema and refuses schema copies
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 2 (check.py already imports `results`) and step 3 (steps.py holds no copy any more, else the copy guard is red).

In `plugins/sdlc-lite/scripts/check.py`, add two guards and a docstring item for them.

The first guard checks the result schema against the agent bodies:
- For each role in `results.SCHEMA`, read `agents/<role>.md`. Every declared section must appear as a line exactly `## <Section>` (rstripped), and their first occurrences must be in the declared order.
- A failure appends `agents/<role>.md: result schema: <what>`, for example `missing ## Checks` or `## Checks before ## Changes`, so the printed line starts `FAIL agents/<role>.md: result schema`.
- Add an inline negative control: the builder body with `## Changes` and `## Checks` swapped must be flagged, else append `check.py: result-schema agent guard negative control not flagged`.
- The current bodies already satisfy this. Verified: builder 24/27/30/33, verifier 25/30/33/36, plan-reviewer 41/44/50, planner 64/80/86, and every other role matches in order.

The second guard keeps the table in one place:
- `scripts/run.sh` must not match the regex `allowed='|sect=[A-Z]`, and `scripts/steps.py` must not match the regex below.

```
REVIEW_VERDICTS|startswith\('inherited red:'\)|first_word\(path, '(Status|Verdict)'
```

- A match appends `scripts/<file>: holds a copy of the result schema`.
- Add an inline negative control: run.sh text with an appended `allowed='x'` line must be flagged.

### Acceptance criteria
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c 'import sys,pathlib; p=pathlib.Path(sys.argv[1]); s=p.read_text(); p.write_text(s.replace("## Changes", "## TMPX").replace("## Checks", "## Changes").replace("## TMPX", "## Checks"))' "$t/p/agents/builder.md" && out=$(python3 "$t/p/scripts/check.py" "$t/p"); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'FAIL agents/builder.md: result schema'`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && printf "%s\n" "# allowed='x'" >>"$t/p/scripts/run.sh" && out=$(python3 "$t/p/scripts/check.py" "$t/p"); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$out" | grep -qF 'FAIL scripts/run.sh: holds a copy of the result schema'`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/scripts/traces/selftest.py | { ! grep -q .; }`

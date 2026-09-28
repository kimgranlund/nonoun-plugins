## Task goal
A verifier output with no pass/fail verdict is reported as an error (no verdict), reruns the verifier, and never counts as a build fail.

## Step 1: steps.py next routes a no-verdict verifier to reverify, and the selftest proves it
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- Add a helper, for example `verdict_or_none(path)`. It returns `'pass'` or `'fail'` when the first non-blank line under `## Verdict` is one of those. It returns `None` when the section is missing or its first line is anything else. It never raises.
- In `next_action`, after the newest verifier `v` is known to count after the newest build `b`, and before the pass and plan-defect checks: if `v` has no verdict, count the consecutive no-verdict results. Walk `order.ordered(d, 'verifier')` backwards from `v`, keeping only verifiers where `order.counts_after(w, b)`, and stop at the first one that has a verdict.
  - Count 1 → return `('reverify', result_level(v), '<basename of v> has no verdict (pass/fail) under ## Verdict; rerun the verifier at the same level', read)`.
  - Count 2 or more → return `('stop', None, '<count> consecutive verifier results with no verdict at build L<level> (newest <basename>); ask the user', read)`.
- In the fail-counting loop, skip any verifier with no verdict. It is neither counted nor an error, so a no-verdict result earlier in the history never raises the count and never exits 1.
- Update the module docstring's `next` rules:
  - Add the `reverify L<n>` rule and the "2+ consecutive no-verdict → stop" rule.
  - State that no-verdict results are never counted as fails.
  - Remove "a verifier with no pass/fail Verdict" from the Errors list.
- In `selftest()`:
  - Replace `next_refused('next error: a verifier with no pass/fail Verdict', ...)` with a `nxt(..., 'reverify L1')` case, using builder-L2 done plus a verifier whose body is only `Nothing to do until the test gate reports.`.
  - Add a case where two consecutive no-verdict verifiers after the same build give `stop`.
  - Add a case where a no-verdict result followed by a real fail at L2 gives `rebuild L2`.
  - Add a case where a no-verdict result followed by a pass gives `done`.
  - Add a case where a fail, a rebuild, a fail, then a no-verdict at L2 gives `reverify L1`, not `bump`.

Write the failing selftest cases in the same change as the fix.
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf 'Nothing to do until the test gate reports.\n' > "$d/verifier-L1.md" && printf '{"file": "builder-L2.md"}\n{"file": "verifier-L1.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" > "$d/out" && head -1 "$d/out" | grep -qx 'reverify L1' && grep -q '^reason: .*verifier-L1.md' "$d/out"`
- `d=$(mktemp -d) && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf 'Nothing to do.\n' > "$d/verifier-L1.md" && printf '## Notes\nhm\n' > "$d/verifier-L1-2.md" && printf '{"file": "builder-L2.md"}\n{"file": "verifier-L1.md"}\n{"file": "verifier-L1-2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'stop'`
- `d=$(mktemp -d) && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf 'Nothing to do.\n' > "$d/verifier-L1.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' > "$d/verifier-L1-2.md" && printf '{"file": "builder-L2.md"}\n{"file": "verifier-L1.md"}\n{"file": "verifier-L1-2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'rebuild L2'`
- `! grep -q "next error: a verifier with no pass/fail Verdict" plugins/sdlc-lite/scripts/steps.py`
- `grep -q "reverify" plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`

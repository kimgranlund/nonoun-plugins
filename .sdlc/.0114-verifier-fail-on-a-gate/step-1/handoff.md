## Task goal
A gate that is already red at the pre-build HEAD is reported as inherited whether the builder or the verifier finds it, so it never costs a rebuild, a level bump, or a replan.

## Step 1: Route, render, and accept the verifier `inherited red:` verdict in the scripts
level: L3
### Do
- `plugins/sdlc-lite/scripts/steps.py`:
  - `verdict_or_none` (and anything it feeds) returns `'inherited'` when the first non-blank line under `## Verdict` starts with `inherited red:` (any case), the same as `build_status_or_none` does for the builder.
  - A bare `inherited red` with no colon stays a no-verdict, so it routes to `reverify`.
  - In `next_action`, after the no-verdict branch and before the `pass`/`plan defect`/fail counting, a newest verifier that counts after the build and has the verdict `inherited` returns `('inherited', None, <reason naming the verifier file and "gate already red at the pre-build HEAD">, read)`.
  - An inherited verdict never counts as a fail in the counting loop and never counts as a no-verdict run. It also breaks the consecutive no-verdict count, the way a real verdict does.
  - Update the `next` rules in the module docstring with the new line.
  - Add selftest cases:
    - done builder, then verifier `inherited red: test_a`, gives `inherited`.
    - verifier with a bare `inherited red` gives `reverify L1`.
    - done, fail, rebuild, then an inherited verifier gives `inherited`, not `bump`.
    - an inherited verifier, then a rebuild and a `fail` verifier at the same level, gives `rebuild L2`, not `bump`. The inherited verdict never counts as a fail.
    - an existing `fail` still gives `rebuild L2`.
  - Selftest fixture strings use the form `'## Verdict\ninherited red: test_a\n'`.
- `plugins/sdlc-lite/scripts/board.py`:
  - In `step_row`, a newest verifier that counts after the build and whose Verdict starts with `inherited red:` renders `'🔴', 'inherited red · builder <L> · verifier <L>, ask the user<tries>'`.
  - The no-verdict counting loop treats `inherited red:` as a verdict.
  - Update the module docstring.
  - Add a selftest case with the fixture string `'## Verdict\ninherited red: test_a\n'`.
- `plugins/sdlc-lite/scripts/run.sh`:
  - Change the verifier's allowed value to `pass|fail|inherited red: .+`.
  - Update the header comment near line 18.
- `plugins/sdlc-lite/scripts/run-selftest.sh`:
  - Add `want_rc 0 verifier L1 $'## Verdict\ninherited red: test_a'`.
  - Add `want_rc 3 verifier L1 $'## Verdict\ninherited red'`.
### Acceptance criteria
- `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\ninherited red: test_a\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" >"$d.out" && test "$(head -1 "$d.out")" = inherited`
- (guard) `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\nfail\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = "rebuild L2"`
- (guard) `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\ninherited red\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && test "$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1)" = "reverify L1"`
- `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\ninherited red: test_a\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && python3 -c "import sys,pathlib; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import board; r=board.step_row(pathlib.Path(sys.argv[1]),'x','L2'); sys.exit(0 if r[0]=='🔴' and r[1].startswith('inherited red') else 1)" "$d"`
- (guard) `d=$(mktemp -d)/s && mkdir -p "$d" && printf '## Status\ndone\n' >"$d/builder-L2.md" && printf '## Verdict\nfail\n' >"$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' >"$d/runs.jsonl" && python3 -c "import sys,pathlib; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import board; r=board.step_row(pathlib.Path(sys.argv[1]),'x','L2'); sys.exit(0 if r[0]=='🔴' and r[1].startswith('fail') else 1)" "$d"`
- `grep -q 'Verdict\\ninherited red: ' plugins/sdlc-lite/scripts/steps.py`
- `grep -q 'Verdict\\ninherited red: ' plugins/sdlc-lite/scripts/board.py`
- `grep -q "want_rc 0 verifier L1 .*inherited red: " plugins/sdlc-lite/scripts/run-selftest.sh`
- `grep -q "want_rc 3 verifier L1 .*inherited red'$" plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`

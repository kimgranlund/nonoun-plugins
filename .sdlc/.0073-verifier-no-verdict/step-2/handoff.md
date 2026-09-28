## Task goal
A verifier output with no pass/fail verdict is reported as an error (no verdict), reruns the verifier, and never counts as a build fail.

## Step 2: board.py renders a no-verdict verifier as 🟡 no verdict, not 🔴 fail
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py` `step_row` (around line 110): when the newest verifier counts after the last build, keep the existing pass and fail branches but gate them on the Verdict's first line.
- A first line starting `pass` stays 🟢 pass.
- A first line starting `fail` stays 🔴 fail.
- Anything else, including a missing section, returns `'🟡', f'no verdict · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}, rerun verify{tries}', LADDER['built']`.

Because `--summary` counts 🔴 rows, this row also drops out of the `🔴<n>` count. Update the module docstring so the Verdict mention says a verifier with no pass/fail verdict renders as 🟡 no verdict. In `selftest()` section 7, add a case: builder done, then a verifier whose body is only `Nothing to do until the test gate reports.`, gives a row whose glyph is 🟡 and whose status starts `no verdict`.
### Acceptance criteria
- `r=$(mktemp -d) && mkdir -p "$r/t/step-1" && printf '## Goal\ng\n' > "$r/t/handoff.md" && printf '## Step 1: x\nlevel: L2\n' > "$r/t/step-1/handoff.md" && printf '## Status\ndone\n' > "$r/t/step-1/builder-L2.md" && printf 'Nothing to do until the test gate reports.\n' > "$r/t/step-1/verifier-L1.md" && printf '{"role": "builder", "file": "builder-L2.md"}\n{"role": "verifier", "file": "verifier-L1.md"}\n' > "$r/t/step-1/runs.jsonl" && SDLC_BOARD_STATE_DIR="$r/state" python3 plugins/sdlc-lite/scripts/board.py --root "$r" --task t > "$r/out" && grep -q 'no verdict' "$r/out" && ! grep -q '🔴' "$r/out" && ! SDLC_BOARD_STATE_DIR="$r/state" python3 plugins/sdlc-lite/scripts/board.py --root "$r" --summary | grep -q '🔴'`
- `grep -q "no verdict" plugins/sdlc-lite/scripts/board.py`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`

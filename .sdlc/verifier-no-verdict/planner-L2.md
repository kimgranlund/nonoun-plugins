<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
A verifier result with no pass/fail verdict gets its own `steps next` action, `reverify L<n>`, which reruns the verifier at the same level. It never counts as a fail, a second consecutive one at the same build stops, and the board shows it as 🟡 no verdict instead of 🔴 fail.

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

## Step 3: /chain, conductor, and repo docs describe the reverify action
level: L1
### Do
- `plugins/sdlc-lite/skills/chain/SKILL.md`, section 4:
  - In the `steps.py next` paragraph (line 30), add `reverify` → verifier at that level to the action list.
  - In rule 4 (or a new sentence next to it), state the rule: a verifier result with no pass/fail `## Verdict` is "no verdict". It reruns the verifier at the same level, is never a fail, never counts toward "a second fail", and never adds `## Previous attempt`. A second consecutive no-verdict at the same build is a stop, so ask the user.
- `plugins/sdlc-lite/agents/conductor.md` line 22: add the same rule in one clause: verifier with no verdict → `reverify` at the same level, never counted as a fail, and a second in a row → stop.
- Repo `CLAUDE.md` `scripts/steps.py` bullet:
  - Add `reverify` to the listed `next` actions.
  - Drop "or result" from the error clause only as far as a no-verdict verifier is concerned. A builder with no Status still errors.
  - Add that a no-verdict verifier result is never counted as a fail and that two in a row stop.
- `.claude/agents/sdlc-lite-author.md`: add a one-line invariant that a verifier result with no verdict maps to `reverify` in `steps.py next` and to 🟡 no verdict in `board.py`, is never counted as a fail, and must stay in sync across steps.py, board.py, chain SKILL.md, conductor.md, and CLAUDE.md.

Do not use em dashes.
### Acceptance criteria
- `grep -q 'reverify' plugins/sdlc-lite/skills/chain/SKILL.md && grep -q 'no verdict' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q 'reverify' plugins/sdlc-lite/agents/conductor.md`
- `grep -q 'reverify' CLAUDE.md`
- `grep -q 'reverify' .claude/agents/sdlc-lite-author.md`
- `! git diff HEAD -- plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/agents/conductor.md CLAUDE.md .claude/agents/sdlc-lite-author.md | grep '^+' | grep -q '—'`
- (guard) `plugins/sdlc-lite/scripts/check.sh`

## Risks
- The action name `reverify` is a choice this plan makes. The ticket gives it only as an example. Any peer tooling that parses `steps next` output will see a new first-line token.
- "Consecutive" counts only verifiers after the newest build. A no-verdict result, then a rebuild, then another no-verdict gives `reverify`, not `stop`. That is intended, because each build gets one rerun.
- The step 3 em-dash criterion checks the diff against HEAD, so it assumes steps 1 and 2 are not committed in between. If they are committed, the check still covers only the doc files, so it holds either way.

## Task goal
A solo L2 ticket whose acceptance criteria are all mechanical and each carry an observed-red control closes on green criteria with no independent verifier; the verifier runs by exception. A measured pilot over the next 20 qualifying tickets decides whether it stays.

## Step 2: solo.md rule, gate field in solo_stats.py, references, gates green
level: L2
guard timeout: 2700
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: step 1.

`plugins/sdlc-lite/agents/solo.md` (one writer). Both additions are affirmative sentences, so the prompt_lint P-6 prohibition count stays at or below base (19 now).
- Loop step 2, the `(red)` sentence: after `specgate.py red` exits 0, solo also runs `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/redck.py" record <task dir>/handoff.md` before the first edit. It writes each control to `red-checkpoint.jsonl`. `specgate.py red` writes no record (`specgate.py:153`), and the tests-gate `red-control` condition reads that file.
- `## Verification`: one line stating that when `verify_scope.py` prints `tests-gate` and exits 0, solo ends its report with `verify: skipped (tests-gate; criteria green, red controls pre-edit)` and still lists every span with its exit code, which `tickets.py close` re-checks against the report file.
- Regenerate with `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. `check.py` compares `solo.md` to `agents/solo-L<n>.md` byte for byte, and the three `adapters/codex/agents/sdlc-solo-l<n>.toml` files carry it. Never edit generated files by hand.

`plugins/sdlc-lite/scripts/solo_stats.py`:
- Add count keys `gate_tests_only` and `gate_verifier`.
- `gate_tests_only`: the ticket's `skips.md` holds `reason: tests-gate diff against` (the line step 1 writes).
- `gate_verifier`: the ticket has at least one verifier round, which is the existing `verified` condition.
- `render` prints two lines that start `gate: tests-only` and `gate: verifier`, each followed by spaces and the count.
- `--json` carries both keys.
- Update the docstring key list.
- Add selftest cases for both values, including a control where the skip line is absent.

References:
- `docs/references/sdlc-internals.md`: in the `verify_scope.py` section (line 57), add the tests-gate class, its nine conditions, the pilot flag and the `--report` option. In the `solo_stats.py` section (line 77), add the two keys.
- `plugins/sdlc-lite/AGENTS.md` line 59: name the tests-gate cases next to the docs-only skip check.

Not changed: `lanes.py` (see Assumptions) and `docs/kpi/005-solo-first-pass-rate.md`.

Then run every gate below, plus `python3 scripts/check-packaging.py` and `git diff --check`, and fix any red that step 1 or this step introduced.
### Acceptance criteria
- `f=plugins/sdlc-lite/agents/solo.md; grep -qF "tests-gate" "$f" && grep -qF "redck.py" "$f" && grep -qF "verify: skipped (tests-gate" "$f"`
- `f=plugins/sdlc-lite/scripts/solo_stats.py; python3 "$f" selftest && grep -qF "gate: tests-only" "$f" && grep -qF "gate: verifier" "$f"`
- `out=$(python3 plugins/sdlc-lite/scripts/solo_stats.py stats .) && printf "%s\n" "$out" | grep -qE "^gate: tests-only +[0-9]+" && printf "%s\n" "$out" | grep -qE "^gate: verifier +[0-9]+"`
- `grep -qF "tests-gate" docs/references/sdlc-internals.md && grep -qF "tests-gate" plugins/sdlc-lite/AGENTS.md`
- (guard) `t=$(mktemp); git show "$SDLC_BASE_SHA":plugins/sdlc-lite/agents/solo.md > "$t"; b=$(python3 plugins/sdlc-lite/scripts/prompt_lint.py "$t" | sed -n "s/.*prohibitions \([0-9]*\),.*/\1/p"); n=$(python3 plugins/sdlc-lite/scripts/prompt_lint.py plugins/sdlc-lite/agents/solo.md | sed -n "s/.*prohibitions \([0-9]*\),.*/\1/p"); test -n "$b" && test -n "$n" && test "$n" -le "$b"`
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 plugins/sdlc-lite/scripts/prompt_lint.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/verify_scope.py -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/scripts/solo_stats.py -e plugins/sdlc-lite/agents/solo.md -e plugins/sdlc-lite/agents/solo-L1.md -e plugins/sdlc-lite/agents/solo-L2.md -e plugins/sdlc-lite/agents/solo-L3.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l1.toml -e plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l2.toml -e plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l3.toml -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/AGENTS.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

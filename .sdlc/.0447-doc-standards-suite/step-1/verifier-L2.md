<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) selftest prints `gate P-1` to `gate P-6: positive ok, negative ok`: pass. Evidence: I ran the criterion command and it exited 0. The output shows gates P-1 to P-6 plus `gate exit` each as "positive ok, negative ok", then `prompt_lint selftest: PASS`. The negatives bite: planted defects in a copy of the plugin under the tmp prefix were flagged by P-1 (`rule 99`, `rule 77` in a generated -L file), P-2 (bad subcommand and bad flag, inline and fenced), P-3 (missing `${CLAUDE_PLUGIN_ROOT}` path and bare `scripts/coverage_check.py`), P-4 (renamed `### Gap defaults`) and P-5 (`## Status` set to `bogusstatus`). The pre-edit red control for this criterion was recorded in `step-1/red-checkpoint.jsonl` (exit 2).
- #2 (red) the lint over agents, skills and overlays exits 0: pass. Evidence: the command exits 0 and prints `prompt_lint: 72 files, 0 errors, 8 warnings`. The 8 warnings are all P-5, for the roles the handoff names as lacking the predicate. Pre-edit red is recorded (exit 2).
- #3 (red) planner.md gets a `warning P-5` line and an `info P-6` line, exit 0: pass. Evidence: the criterion command exits 0. Output is `warning P-5 plugins/sdlc-lite/agents/planner.md: no "closed step" or "closed ticket" line`, then `info P-6 ...: prohibitions 40, NEVER 0, vague 0`, and the summary line reads 0 errors, 1 warning. Pre-edit red is recorded.
- #4 (red) check.sh holds `prompt_lint.py" selftest`: pass. Evidence: the grep exits 0. The diff adds `python3 "$root/scripts/prompt_lint.py" selftest || fail=1` after the docs_check.py selftest line and names prompt_lint.py in the header comment.
- #5 (red) check.py has item 53 and `import prompt_lint`: pass. Evidence: the python assert exits 0. The diff adds the docstring item "53. Prompt references (T-0447)" and code after item 52. A check.py run on a plugin copy with planted defects printed `FAIL check.py: prompt references: error P-1 overlays/builder.md ... "rule 99"` and the P-2 and P-3 errors for the planted flag and bare path, and exited non-zero. So the item bites on all three planted defect types.
- #6 (red) both architect files use `skills/decompose/scripts/coverage_check.py`: pass. Evidence: the loop exits 0 with no FAIL lines. The diff shows `${CLAUDE_PLUGIN_ROOT}/skills/decompose/scripts/coverage_check.py` on line 15 of agents/architect.md and line 15 of skills/architect/SKILL.md. "Markdown-only design" and `coverage_check.py` are kept. `check.py plugins/sdlc-lite` exits 0, so the pin at check.py:752 still holds.
- #7 (red) AGENTS.md names `prompt_lint.py`: pass. Evidence: the grep exits 0. The diff adds one Verification line naming `python3 plugins/sdlc-lite/scripts/prompt_lint.py` and `selftest`.
- #8 (red) prompt_lint.py exists with no en or em dash and no trailing whitespace: pass. Evidence: the python assert exits 0.
- #9 (guard) `claude_roles.py generate --check`: pass. Evidence: output `Claude agent definitions verified (22 files)`, exit 0.
- #10 (guard) `codex_roles.py generate --check`: pass. Evidence: output `Codex agent definitions verified`, exit 0.
- #11 (guard) scope diff against `$SDLC_BASE_SHA`: pass. Evidence: the `test -z` command exits 0. `git status` lists only the allowed files, and the other changes are under `.sdlc`.
- Extra checks of the handoff's spec, all met. The CLI exits 2 on a usage error (`--bogus` and a nonexistent file both gave rc=2). It exits 1 on any error (rc=1 with planted defects). A run with no FILE argument scans the 72 default files. The module docstring names the upstream prompt-wording-rules skill as prior art (lines 29-30). `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` prints `ok: 19 role levels, 9 agents, 22 generated definitions checked`, exit 0. Findings print as `<level> <rule> <path>: <message>` with the path as given.

## Out of scope changes
None. The builder reported two choices beyond the handoff text:
- P-2 in fenced blocks counts a script only in command position.
- P-3 skips paths that contain `>` or are made only of dots.

I checked both. The fenced rule still flags fenced `python3 steps.py zzz-sub --nope` (P-2 errors on lines 92 of the planted copy), and the handoff allows fixing the lint rather than a reference that exists. The skipped paths are placeholders. Both are inside prompt_lint.py, which this step creates.

Harmless: `results.key(role)` does not exist, and the lint reads `results.SCHEMA[role]['key']`, which holds the same value. I confirmed that key in the `results.SCHEMA` output above.

## For the next attempt
None

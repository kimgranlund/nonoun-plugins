<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 selftest prints the 12 named controls: pass. Evidence: `report.py selftest` exited 0, 34 output lines, all 12 `ok: control <name>:` lines present; the criterion's own loop returned rc 0. Bite check: copied report.py to a throwaway dir under the tmp prefix and broke the real rules. Newest-snapshot by mtime gave `FAIL: control compare last` and `selftest: 1 failed`. `_pid_alive` always True gave `FAIL: control dead pid`. Each control also swaps its rule for a no-op and requires red (report.py:1556-1568). No `process-deviations.md` exists; `red-checkpoint.jsonl` holds 8 pre-edit red controls and an `audit` line with `status: ok`.
- #2 `render nosuchview` exits 2 and stderr lists all views and options: pass. Evidence: criterion command rc 0. Stderr was `views: summary full tasks signals needs context cost children identity evidence` and `options: --since --last --next --only --severity --format --evidence --compare --explain --no-snapshot (--session is reserved and refused)`. Live `--bogus` and `--session x` both exit 2 with the same lists.
- #3 summary has 1 to 8 lines: pass. Evidence: criterion rc 0. The live summary is 7 lines with no header (state, needs, now, next, recent, grade, unknown).
- #4 `render full` prints the section headers: pass. Evidence: criterion rc 0. The live output shows `summary: tasks: signals: context: cost: children: identity: evidence:` as exact lines, in the handoff order.
- #5 JSON shape: pass. Evidence: criterion rc 0. `schema` is `session-status/1`, the nine groups are present, and `health.context` has all 7 keys. Cost reads `dollars 4.4536`, `priced 2`, `unpriced 0`. `unknown` is a list of dotted paths (5 entries). The "unknown cost" and "an unpriced run reads unpriced, not $0" selftest cases back the unknown-not-zero rule.
- #6 `report.VERBS` has 11 verbs and all are in core.md: pass. Evidence: criterion rc 0. The tuple is built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting.
- #7 exact verb line in core.md: pass. Evidence: grep rc 0. `git diff` shows the new `## Status verbs` section after `## Status words`, with the verb line and the tense rule.
- #8 glossary row: pass. Evidence: grep rc 0. `git diff` shows the new `| status verb | noun | ... |` row.
- #9 `docs_check.py --root .`: pass. Evidence: `docs_check: 0 errors, 26 warnings`. The 26 are all in files this step did not touch. The exit code printed blank because `PIPESTATUS` is zsh-specific, but the 0-errors line stands.
- #10 scope: pass. Evidence: with `SDLC_BASE_SHA=ebac4973`, the criterion command returned rc 0. `git status` outside `.sdlc` shows only `M glossary.md`, `M core.md` and `?? report.py`. `git diff --check` is clean.

Other checks:
- Python 3.9.6 runs it (the host `python3`).
- `CLAUDE_PID=999999` live gives `state: dead`.
- No snapshot was written under `.sdlc/runtime/` (only the existing `prune.*`) when `--no-snapshot` is used.
- Steelman: I considered failing for the extra `recent:` and `unknown:` summary lines and for the unlisted `stalled` state. The handoff allows both (at most 8 lines; the handoff itself names `stalled`), so I dropped that finding.

## Out of scope changes
None. The only tree changes outside `.sdlc` are `plugins/sdlc-lite/scripts/report.py`, `docs/specs/doc-standards/core.md` and `docs/references/glossary.md`, confirmed by criterion #10 and `git status`.

## For the next attempt
None

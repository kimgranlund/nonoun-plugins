<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `supervisor.py selftest | grep -q 'ok: codex prompt names the absolute script path'`: pass. Evidence: rerun on the built tree prints `ok: codex prompt names the absolute script path and no message text`, exit 0. The negative control runs inside that case (`CTL_PATHLESS_PROMPT`, diff lines in supervisor.py). I also mutated a temp copy of `scripts/` to drop the path sentence from `wake_prompt`. Its selftest went `FAIL` (`prompt: no body and no topic ... expected the fixed text`), so the prompt checks go red without the path. The mutation failed in an earlier case, so it did not isolate the new case's own control.
- `wake_prompt('bob', 1)` contains the absolute `messages.py` path plus `count` and `ack`: pass. Evidence: the python assert exits 0 (AC2=0).
- `codex-rerun-1.txt` last line matches `^result=(pass|fail|unverified)`: pass. Evidence: last line `result=pass`.
- `codex-rerun-2.txt` last line matches `^result=(pass|fail|unverified)`: pass. Evidence: last line `result=pass`.
- `codex-rerun-3.txt` last line matches `^result=(pass|fail|unverified)`: pass. Evidence: last line `result=pass`.
- k sentence in the record and README: pass. Evidence: computed k=3. `Codex wake arm after the fix: 3 of 3 passed.` is in `docs/reports/supervisor-live-run.md` (new section, before Limits) and in `docs/README.md` (T-0183 line). The grep exits 0.
- Known-limit conditional: pass. Evidence: all three last lines are `result=pass`, so the condition does not apply and the `if` is vacuously true. It is not a bite-able check here, but k=3 means no limit line is required.
- No `Codex pass` when any rerun failed: pass. Evidence: the condition does not apply (k=3). The README says `Codex pass`, which the formula allows. `Result codex-attached: pass` (line 269) and `Result codex-push: pass` (line 372) are in the record. The four Claude arms (dry-run, claude, claude-attached, claude-push) are all `pass` (lines 309, 144, 184, 337), so `Claude Code pass` follows the formula.
- (guard) `supervisor.py selftest`: pass. Evidence: `supervisor selftest: PASS`.
- (guard) `probe.py selftest`: pass. Evidence: `probe selftest: PASS`.
- (guard) no em dash in supervisor.py, supervisor-live-run.md, README.md: pass. Evidence: the grep exits 0. A count of em dashes in `AGENTS.md` and the three rerun files is 0 each.
- (guard) scope guard with `SDLC_BASE_SHA=3ac65cd...`: pass. Evidence: the command exits 0 (`scope=0`).

Builder claims I checked:
- All three reruns show `wakes=1`, `remote_commits_added=0`, `pre_push_calls=0`, `push_attempt=absent` (grep of the evidence files).
- `git diff --check` is clean.
- Git shows no change to `codex.txt`, `probe.py` or `messages.py` (empty `git diff --name-only` for those paths).
- The three rerun files are untracked new files. Their format is consistent with the probe's output. Hand edits cannot be disproven from the tree, but the contents match the probe's output shape.
- The six other arms were not rerun on the fixed prompt. The record's Limits section states this.

Steelman of a possible fail (the README's `Claude Code pass` and `Codex pass` rest on old-prompt results for the other arms): the builder's rebuttal is that the handoff's formula specifies exactly those `Result` lines. I read the handoff and the formula matches. Dropped.

## Out of scope changes
None. The changed set is exactly `supervisor.py`, `supervisor-live-run.md`, `supervisor-live-run/AGENTS.md`, `README.md`, and `codex-rerun-{1,2,3}.txt`. The scope guard passes. The `.sdlc/` step artifacts are excluded by the guard.

## For the next attempt
None

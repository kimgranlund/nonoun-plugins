<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `import hashlib` and a `follow_digest(items)` helper (sha256 of the full ordered bullet texts, first 12 hex characters). `cmd_close` gains `expect=None`. `--skip` without `--expect` now refuses, and so does an `--expect` that does not match. `--reason` also refuses with `--expect`. The dry run ends with an `expect <digest>` line. The close parser gets `--expect DIGEST`, and main passes it through. The module docstring and help texts are updated. Selftest cases (p), (q), (r) and (t) are adjusted, and a new case (v) covers v1 to v5.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: `tickets selftest: PASS`.
- Negative control: in a scratch copy of the whole plugin, I changed `expect.strip() != digest` to `False`. Its selftest printed `FAIL`, naming (v1) and (v5). The real file was not changed.
- Temp git repo, ticket `alpha` with 3 follow-ups:
  - `close alpha --dry-run` ends with `expect f3ca90f5959b`, which matches `^expect [0-9a-f]{12}$`.
  - `close alpha --skip 2`: rc=1, stderr ends with `nothing written`.
  - After reordering the list and committing, `close alpha --skip 2 --expect <old>`: rc=1, stderr says `does not match ... nothing written`, and `git status --short` is empty.
  - After restoring the list, `close alpha --skip 2 --expect <digest>`: rc=0, 2 follow-ups filed.
- `tickets.py close --help` lists `--expect DIGEST`.
- `grep -n expect tickets.py | head` shows `--expect` on the Usage line (5) and in the close paragraph (lines 30 to 32).
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
- The (v) selftest block sits before (u) in the source. Only the labels are out of order; behavior is not affected.
- This step does not cover the /file SKILL.md pass-through or the CLAUDE.md tickets.py line from the task goal. Those are later steps.
- The first attempt at the negative control copied only `scripts/*.py` and crashed with FileNotFoundError, because the copy had no templates. It had to copy the whole plugin; the `sed` edit is unchanged.

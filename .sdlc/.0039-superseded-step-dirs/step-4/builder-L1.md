<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None. The audit found nothing that needed changing.

## Checks
- `grep -rn 'step-' plugins/sdlc-lite .claude` over `*.sh`, `*.py`, `*.md`, excluding `bench/tasks` and `bench/results`. I reviewed every hit:
  - Live-step-only readers, which skip superseded dirs:
    - `bench-summary.sh:13-16` filters with `^step-[0-9]+$`.
    - `board.py:55-56` (the step-dir helper) uses `fullmatch(r'step-\d+')`.
  - Intentionally inclusive readers, which still count superseded dirs:
    - `bench-summary.sh:26` (cost).
    - `board.py:61-62` (cost).
    - `board.py:196-198` (`has_step_work`).
  - Reader that never sees a superseded dir: `statusline.sh:46`, which reads `step-[0-9]*` from a running-role path, so it only names the step number.
  - Fixtures and docs: the `tickets.py` selftest strings, the `board.py` selftest fixtures, `agents/filer.md`, `skills/chain/SKILL.md` and `skills/handoff-format/SKILL.md`.
- No step counter exists in `bench.sh` or in `skills/*` beyond the documented `chain` and `handoff-format` text.
- Neither `plugins/sdlc-lite/CLAUDE.md` nor `.claude/agents/sdlc-lite-author.md` describes step globbing or step dirs, so neither needed an edit.
- `plugins/sdlc-lite/scripts/check.sh` passed. The role-level, tickets, board and run selftests, shellcheck and plugin validate all reported ok. Only the tail was shown, and its `rc=0` is `tail`'s exit code, not `check.sh`'s.

## Notes
None

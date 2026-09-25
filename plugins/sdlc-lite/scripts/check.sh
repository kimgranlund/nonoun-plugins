#!/usr/bin/env bash
# Plugin checks: level-table and agent consistency, the coverage_check, tickets.py, board.py,
# steps.py, order.py, and fanout.py selftests (fanout: throwaway repos and a stub driver, no model
# call), the run.sh result-numbering selftest (stub claude, no model call), the hook selftest
# (block-background.sh and block-publish.sh on fixture JSON), a shellcheck pass,
# plugin manifest validation.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
python3 "$root/scripts/check.py" "$root" || fail=1
python3 "$root/skills/decompose/scripts/coverage_check.py" selftest || fail=1
python3 "$root/scripts/tickets.py" selftest || fail=1
python3 "$root/scripts/board.py" selftest || fail=1
python3 "$root/scripts/steps.py" selftest || fail=1
python3 "$root/scripts/order.py" selftest || fail=1
python3 "$root/scripts/fanout.py" selftest || fail=1
bash "$root/scripts/run-selftest.sh" || fail=1
bash "$root/scripts/hook-selftest.sh" || fail=1
if command -v shellcheck >/dev/null; then
  shellcheck --severity=warning "$root"/scripts/*.sh "$root"/hooks/*.sh && echo "ok: shellcheck" || fail=1
else
  echo "skip: shellcheck not installed"
fi
if claude plugin validate "$root" >/dev/null 2>&1; then echo "ok: plugin validate"; else echo "FAIL: claude plugin validate"; fail=1; fi
exit $fail

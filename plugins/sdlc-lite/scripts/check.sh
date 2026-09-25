#!/usr/bin/env bash
# Plugin checks: level-table and agent consistency, the coverage_check, tickets.py and board.py
# selftests, the run.sh result-numbering selftest (stub claude, no model call), a shellcheck
# pass, plugin manifest validation.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
python3 "$root/scripts/check.py" "$root" || fail=1
python3 "$root/skills/decompose/scripts/coverage_check.py" selftest || fail=1
python3 "$root/scripts/tickets.py" selftest || fail=1
python3 "$root/scripts/board.py" selftest || fail=1
bash "$root/scripts/run-selftest.sh" || fail=1
if command -v shellcheck >/dev/null; then
  shellcheck --severity=warning "$root"/scripts/*.sh "$root"/hooks/*.sh && echo "ok: shellcheck" || fail=1
else
  echo "skip: shellcheck not installed"
fi
if claude plugin validate "$root" >/dev/null 2>&1; then echo "ok: plugin validate"; else echo "FAIL: claude plugin validate"; fail=1; fi
exit $fail

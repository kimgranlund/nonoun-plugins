#!/usr/bin/env bash
# Plugin checks: level-table and agent consistency, the coverage_check, tickets.py, board.py,
# results.py, evals.py, proposals.py, steps.py, order.py, fanout.py, gate_lock.py, onboard.py, traces.py, messages.py, footprint.py, fleet_collect.py, fleet_detect.py, fleet_config.py, fleet_status.py, specgate.py, cite_check.py, and supervisor.py selftests (fanout: throwaway repos and a stub driver, no model
# call), the budget.py selftest (per-ticket budget meter), the solo_run.py selftest (solo cost capture; stub claude), the run.sh selftest (result numbering, stream-json result pick, Bash timeout env; stub claude, no model call), the hook selftest
# (block-background.sh with Bash, Agent, and Monitor fixtures, block-publish.sh, block-pattern-kill.sh, block-stray-worktree.sh, block-repo-format.sh, block-disk-scan.sh, and block-role-spawn.sh on fixture JSON), the
# hook live probe selftest
# (hook-live-probe.sh --selftest: offline, a stub claude; the live probe spends a model call and
# never runs here), a shellcheck pass, plugin manifest validation.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
python3 "$root/scripts/codex_roles.py" generate --check || fail=1
python3 "$root/scripts/codex-selftest.py" || fail=1
python3 "$root/scripts/lifecycle-selftest.py" || fail=1
python3 "$root/scripts/check.py" "$root" || fail=1
python3 "$root/skills/decompose/scripts/coverage_check.py" selftest || fail=1
python3 "$root/scripts/tickets.py" selftest || fail=1
python3 "$root/scripts/board.py" selftest || fail=1
python3 "$root/scripts/results.py" selftest || fail=1
python3 "$root/scripts/evals.py" selftest || fail=1
python3 "$root/scripts/proposals.py" selftest || fail=1
python3 "$root/scripts/steps.py" selftest || fail=1
python3 "$root/scripts/order.py" selftest || fail=1
python3 "$root/scripts/fanout.py" selftest || fail=1
python3 "$root/scripts/gate_lock.py" selftest || fail=1
python3 "$root/scripts/onboard.py" selftest || fail=1
python3 "$root/scripts/traces.py" selftest || fail=1
python3 "$root/scripts/messages.py" selftest || fail=1
python3 "$root/scripts/footprint.py" selftest || fail=1
python3 "$root/scripts/fleet_collect.py" selftest || fail=1
python3 "$root/scripts/fleet_detect.py" selftest || fail=1
python3 "$root/scripts/fleet_config.py" selftest || fail=1
python3 "$root/scripts/fleet_status.py" selftest || fail=1
python3 "$root/scripts/specgate.py" selftest || fail=1
python3 "$root/scripts/budget.py" selftest || fail=1
python3 "$root/scripts/solo_run.py" selftest || fail=1
python3 "$root/scripts/inventory.py" selftest || fail=1
python3 "$root/scripts/docs_check.py" selftest || fail=1
python3 "$root/scripts/promote.py" selftest || fail=1
python3 "$root/scripts/cite_check.py" selftest || fail=1
python3 "$root/scripts/plan_check.py" selftest || fail=1
python3 "$root/scripts/supervisor.py" selftest || fail=1
python3 "$root/scripts/rename_refs.py" selftest || fail=1
bash "$root/scripts/run-selftest.sh" || fail=1
bash "$root/scripts/hook-selftest.sh" || fail=1
bash "$root/scripts/hook-live-probe.sh" --selftest || fail=1
if command -v shellcheck >/dev/null; then
  shellcheck --severity=warning "$root"/scripts/*.sh "$root"/hooks/*.sh && echo "ok: shellcheck" || fail=1
else
  echo "skip: shellcheck not installed"
fi
if claude plugin validate "$root" >/dev/null 2>&1; then echo "ok: plugin validate"; else echo "FAIL: claude plugin validate"; fail=1; fi
exit $fail

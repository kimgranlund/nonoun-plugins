#!/usr/bin/env bash
# Plugin checks: level-table and agent consistency, the generated Claude and Codex agent definitions (claude_roles.py, codex_roles.py) and the claude_roles.py selftest, the dispatch.py selftest (prepare parity with the run.sh dry run, gate refusals, attempt records; record parity with a stub-claude run.sh run, invalid and failed results, strays, cleanup), the coverage_check, roots.py, tickets.py, board.py,
# results.py, evals.py, proposals.py, steps.py, redck.py, order.py, fanout.py, gate_lock.py, lanes.py, onboard.py, traces.py, messages.py, footprint.py, fleet_collect.py, solo_stats.py, fleet_detect.py, fleet_config.py, fleet_status.py, report.py, specgate.py, cite_check.py, verify_scope.py, prompt_lint.py (prompt references, one negative per rule), reply_lint.py (reply rules, one observed-red fixture per rule), plan_check.py (the plan-doc rules, one observed mutant per rule), compaction_handoff.py (the compaction handoff section: its three write refusals, replace, clear, and stale status), plan_doc.py, plan_done.py (the plan-doc stop condition, one case per truth-table row), and supervisor.py selftests (fanout: throwaway repos and a stub driver, no model
# call), the budget.py selftest (per-ticket budget meter), the solo_run.py selftest (solo cost capture; stub claude), the run.sh selftest (result numbering, stream-json result pick, Bash timeout env; stub claude, no model call), the hook selftest
# (block-background.sh with Bash, Agent, and Monitor fixtures, block-publish.sh, block-pattern-kill.sh, block-stray-worktree.sh, block-repo-format.sh, block-disk-scan.sh, block-role-write.sh, block-role-rm.sh, close-role-stdin.sh, and block-role-spawn.sh on fixture JSON, with the _role.sh resolver), the
# hook live probe selftest
# (hook-live-probe.sh --selftest: offline, a stub claude; the live probe spends a model call and
# never runs here), the check_pool.py selftest, the wtroot.py selftest (worktree root, owner markers, crash sweep) and the
# migrate-worktrees.sh selftest (the legacy .worktrees/ and .claude/worktrees/ to sibling-root migration on a fixture repo), a shellcheck pass,
# plugin manifest validation.
# Usage: check.sh [--fast] [--jobs N]. The jobs run in parallel through check_pool.py (--jobs N, else SDLC_CHECK_JOBS,
# else the core count), each job's output printed whole in list order, then the failed jobs with the first one named.
# --fast runs only the jobs tagged fast (structure, generated-file parity, the quick selftests): the builder and CI tier.
# The full run, every job, stays the land gate. Jobs are listed slowest first so the long ones start at once.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
tier=full
jobs=""
while [ $# -gt 0 ]; do
  case $1 in
    --fast) tier=fast ;;
    --jobs) jobs=${2:-}; shift ;;
    *) echo "usage: check.sh [--fast] [--jobs N]" >&2; exit 2 ;;
  esac
  shift
done
list="$(mktemp -d "${TMPDIR:-/tmp}/sdlc-check.XXXXXX")" || exit 2
trap 'rm -rf "$list"' EXIT
n=0
job() { # job <fast|full> <name> <command...>: queue one job; --fast leaves out the full ones
  local t=$1
  shift
  [ "$tier" = fast ] && [ "$t" = full ] && return 0
  n=$((n + 1))
  printf '%s\0' "$@" >"$list/$(printf '%03d' "$n")"
}
job full fanout python3 "$root/scripts/fanout.py" selftest
job full traces python3 "$root/scripts/traces.py" selftest
job full dispatch python3 "$root/scripts/dispatch.py" selftest
job full run-selftest bash "$root/scripts/run-selftest.sh"
job full lanes python3 "$root/scripts/lanes.py" selftest
job full messages python3 "$root/scripts/messages.py" selftest
job full supervisor python3 "$root/scripts/supervisor.py" selftest
job full tickets python3 "$root/scripts/tickets.py" selftest
job full gate_lock python3 "$root/scripts/gate_lock.py" selftest
job fast steps python3 "$root/scripts/steps.py" selftest
job fast codex-selftest python3 "$root/scripts/codex-selftest.py"
job fast hook-selftest bash "$root/scripts/hook-selftest.sh"
job fast reorg python3 "$root/scripts/reorg.py" selftest
job fast solo_run python3 "$root/scripts/solo_run.py" selftest
job fast fleet_status python3 "$root/scripts/fleet_status.py" selftest
job fast report python3 "$root/scripts/report.py" selftest
job fast hook-live-probe bash "$root/scripts/hook-live-probe.sh" --selftest
job fast redck python3 "$root/scripts/redck.py" selftest
job fast lifecycle-selftest python3 "$root/scripts/lifecycle-selftest.py"
job fast onboard python3 "$root/scripts/onboard.py" selftest
job fast roots python3 "$root/scripts/roots.py" selftest
job fast check.py python3 "$root/scripts/check.py" "$root"
job fast verify_scope python3 "$root/scripts/verify_scope.py" selftest
job fast docs_check python3 "$root/scripts/docs_check.py" selftest
job fast specgate python3 "$root/scripts/specgate.py" selftest
job fast proposals python3 "$root/scripts/proposals.py" selftest
job fast board python3 "$root/scripts/board.py" selftest
job fast inventory python3 "$root/scripts/inventory.py" selftest
job fast evals python3 "$root/scripts/evals.py" selftest
job fast fleet_collect python3 "$root/scripts/fleet_collect.py" selftest
job fast plan_done python3 "$root/scripts/plan_done.py" selftest
job fast plan_check python3 "$root/scripts/plan_check.py" selftest
job fast results python3 "$root/scripts/results.py" selftest
job fast rename_refs python3 "$root/scripts/rename_refs.py" selftest
job fast prompt_lint python3 "$root/scripts/prompt_lint.py" selftest
job fast order python3 "$root/scripts/order.py" selftest
job fast footprint python3 "$root/scripts/footprint.py" selftest
job fast fleet_detect python3 "$root/scripts/fleet_detect.py" selftest
job fast cost_estimate python3 "$root/scripts/cost_estimate.py" selftest
job fast compaction_handoff python3 "$root/skills/plan/scripts/compaction_handoff.py" selftest
job fast solo_stats python3 "$root/scripts/solo_stats.py" selftest
job fast reply_lint python3 "$root/scripts/reply_lint.py" selftest
job fast promote python3 "$root/scripts/promote.py" selftest
job fast plan_doc python3 "$root/scripts/plan_doc.py" selftest
job fast fleet_config python3 "$root/scripts/fleet_config.py" selftest
job fast coverage_check python3 "$root/skills/decompose/scripts/coverage_check.py" selftest
job fast codex_roles-generate python3 "$root/scripts/codex_roles.py" generate --check
job fast claude_roles python3 "$root/scripts/claude_roles.py" selftest
job fast claude_roles-generate python3 "$root/scripts/claude_roles.py" generate --check
job fast cite_check python3 "$root/scripts/cite_check.py" selftest
job fast budget python3 "$root/scripts/budget.py" selftest
job fast check_pool python3 "$root/scripts/check_pool.py" selftest
job fast wtroot python3 "$root/scripts/wtroot.py" selftest
job fast migrate-worktrees bash "$root/scripts/migrate-worktrees.sh" --selftest
# The repository gate: docs/ conforms to docs/layout.md (this repository only; a consumer install has no docs/layout.md beside it).
if [ -f "$root/../../docs/layout.md" ] && [ -e "$root/../../.git" ]; then job fast docs-repo python3 "$root/scripts/docs_check.py" --root "$root/../.."; fi
if command -v shellcheck >/dev/null; then
  job fast shellcheck shellcheck --severity=warning "$root"/scripts/*.sh "$root"/hooks/*.sh
else
  echo "skip: shellcheck not installed"
fi
job fast plugin-validate claude plugin validate "$root"
python3 "$root/scripts/check_pool.py" run "$list" ${jobs:+--jobs "$jobs"}

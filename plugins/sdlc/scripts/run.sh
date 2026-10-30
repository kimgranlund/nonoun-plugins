#!/usr/bin/env bash
# Usage: run.sh <role> <level> <handoff.md>
# Runs one role headless in the current directory with the level's model and effort.
# Writes <records dir>/<role>-<level>.md (the agent's report) and <role>-<level>.log, where the records dir is
# scripts/order.py records_dir of the handoff dir (<nearest .sdlc>/runtime/tasks/<task>/, or the handoff dir for a
# legacy task dir that already holds records)
# (raw stream-json: one JSON event per line, stderr mixed in). A rerun of the same role and level (a replan, a rebuild) never overwrites: it
# writes <role>-<level>-<k>.md and .log with the lowest free k >= 2, and prints the path it
# wrote; readers take the newest file. Keeps <role>-<level>.running while the run is live
# (for /board and the status line), and appends one line to <records dir>/runs.jsonl for /bench;
# its "file" field names the result, and scripts/order.py orders results by those lines.
# Claude backend runs with --dangerously-skip-permissions; hooks/block-publish.sh still blocks publishing (via SDLC_ROLE). Every role except builder gets Edit/Write/NotebookEdit disallowed.
# Preflight: exits 2 unless the current directory is in a git work tree with at least one commit, and exits 2 when
# .sdlc/config has a plugin_min: line above this plugin's manifest version (scripts/plugin_min.py, T-0593).
# Node: a .nvmrc at the git toplevel is resolved against ${NVM_DIR:-$HOME/.nvm}/versions/node
# (nvm is never sourced or run). An exact version (v20.11.0) matches that dir only; a partial one
# (20, v20.11) matches whole components and takes the highest installed. A match prepends its bin
# dir to PATH, so the role run inherits it; no match or an alias (lts/*, node) leaves PATH alone.
# Each outcome prints one "run.sh: .nvmrc ..." line on stderr; none changes the exit code.
# Result check: after the result and its runs.jsonl line are written (both kept), the result must pass
# scripts/results.py validate --role <role> against the table that results.py schema prints: the header line
# run.sh writes, the role's key section (a line exactly "## <Name>") with an allowed first value where the
# role has one (builder ## Status done|blocked|inherited red: <tests>,
# verifier ## Verdict pass|fail|inherited red: <tests>, plan-reviewer ## Verdict pass|replan|blocked),
# and the declared sections present in declared order. Otherwise one stderr line
# "run.sh: <role> result <reason>; see <file>", exit 3. The result-pick heading comes from results.py key.
# Family rules (Claude backend only; each reads the model= token of the newest result by
# scripts/order.py): a verifier never runs on the newest build's family (a Fable or Sonnet build
# moves it to Opus, an Opus build moves it to Sonnet, same effort), and a plan-reviewer never runs on
# the newest planner result's family (an Opus planner moves it to Fable, a Fable planner to Opus, same
# effort; a Sonnet planner, or no planner result, keeps the row, Fable high). A verifier whose handoff dir holds no builder result (a verifier
# launched at the task dir) reads instead the newest builder result, by scripts/order.py, of the
# highest-numbered step-<n>/ under it that holds one. step-<n>.superseded-<k>/ dirs are left out.
# A verifier whose dir holds no builder result at all reads the model of the newest `role solo` record in
# runs.jsonl (a solo ticket, T-0356): a Sonnet solo moves it to Opus, an Opus solo moves it to Sonnet.
# scripts/codex_roles.py resolve applies the same rule on Codex.
# Throwaway worktrees: a real run (never a dry run) passes the role
# SDLC_TMP_WORKTREES=<worktree root>/tmp/<role>-<pid of run.sh>, a prefix this run owns; the root is wtroot.py root,
# the sibling <main checkout parent>/<name>.worktrees outside the repo (T-0563; the main checkout is the parent of
# git rev-parse --git-common-dir, so a run inside a lane never nests its prefix in the lane, T-0550), or a
# worktree_root: config line or a bare clone's <bare parent>/lanes (T-0561). run.sh
# does not create it; a role makes worktrees only under it (git worktree add --detach "$SDLC_TMP_WORKTREES/<name>"
# HEAD makes the parents). The prompt also names the prefix as a literal path, on a "Throwaway worktrees only under" line (T-0711; a dry run prints the same path, with its own pid). On every exit, success or failure (exit 1, exit 3, INT, TERM, HUP), cleanup
# runs git worktree remove --force on each registered worktree under that prefix (paths compared by
# realpath, since macOS reports /private/var for /var), rm -rf of the prefix, git worktree prune, then
# rmdir of <worktree root>/tmp only when empty. It touches only this run's prefix, never other
# worktrees that appeared during the run (concurrent fanout lanes run other role runs), and never
# changes the exit code; INT, TERM, and HUP exit 130, 143, and 129 after it.
# Prompt TERM: the role runs in the background and run.sh waits on it, since bash defers a trap until
# a foreground child exits. On INT, TERM, or HUP the wait returns at once; the exit handler sends a
# still-running role TERM, waits up to 2 s, sends KILL, and only then cleans up, so a dying role cannot
# recreate files and the handler ends well inside run_lifecycle.py's 5 s grace before its SIGKILL.
# Reaper: a run SIGKILLed anyway skips that cleanup, so a real run also calls
# scripts/reap-tmp-worktrees.sh on <main checkout> at the start (before the stray snapshot) and again
# after removing its own prefix. It removes prefixes under <worktree root>/tmp (and the legacy .claude/worktrees/tmp and .worktrees/tmp)
# whose <pid> names no live
# process, never this run's own, and never changes the exit code.
# Stray report: a real run (never a dry run) snapshots `git worktree list --porcelain` and the local
# branches (refs/heads) before the role starts. Worktrees and branches that appeared during this run
# (from a script, make target, or other program the hooks cannot see) are reported when they belong to
# this role (under <worktree root>/tmp, or on a branch named with this run's prefix $role-$$; sibling lanes
# elsewhere are not, as in dispatch.py record), leaving out this run's own prefix (compared by realpath). This run's runs.jsonl line always holds stray_worktrees
# (array of worktree paths) and stray_branches (array of branch names), empty arrays when none
# appeared. At exit, on success or failure (exit 1, exit 3, INT, TERM, HUP), after the cleanup, stderr
# gets one line per item, once per run: "run.sh: stray worktree appeared during this run: <path>
# [<branch>]" (no " [<branch>]" for a detached worktree) and "run.sh: stray branch appeared during
# this run: <branch>". It says "appeared during this run", not that this role made them, because
# concurrent fanout lanes and other role runs can add worktrees and branches too. It only reports:
# it never removes or deletes anything and never changes the exit code.
# Session limit: when a run fails (exit 1) and its log shows a 429 or a session or usage limit, run.sh writes
# <role>-<level>.limit (one JSON line: ts, role, level, handoff, resume, evidence) beside the result and prints
# "run.sh: session limit: resume with: <command>" on stderr (a log reset time adds a `reset` field and " (resets 1:40pm)"); the exit code stays 1. A later success removes the marker.
# Exit codes: 0 ok, 1 run failed or returned no result (run_lifecycle.py also turns an exit 0 with no
# saved result into 1), 2 usage or preflight, or a spec gate refusal, 3 result fails the result check,
# 4 ticket budget at 80 percent or more with no ack, 5 lane gate (below). A replan cap refusal (below) exits 2.
# Lane gate (T-0274): a planner, builder, or plan-reviewer run on a task or step handoff whose ticket (the task
# handoff has an `id:` line) gets `steps.py lane --check` on its task dir; lane solo prints the exact
# solo_run.py command on stderr and exits 5 before any attempt record. SDLC_LANE_OVERRIDE="<reason>" proceeds,
# appends `lane override: <reason>` once to the task's skips.md, and adds "lane_override" to the runs.jsonl line.
# Not gated: other roles, a task with no ticket id, any lane but solo, a task whose skips.md already ends in a
# non-solo `lane:` record (a chain or fanout recorded its own reason), and fanout's forced-lane runs (it sets
# the override itself).
# Goal precheck: before a planner or plan-reviewer run on a task handoff (not a step dir), run.sh runs
# steps.py precheck on the handoff dir; no ## Goal section prints the reason and exits 2 before any attempt record.
# Replan cap (T-0553): before a planner run (dry runs too, never in the run_lifecycle.py child) whose records dir
# already holds two planner-L*.md results (the first plan and the one replan), run.sh prints two "run.sh: replan cap:"
# lines naming the count and SDLC_REPLAN_APPROVED="<who: why>" and exits 2 before any attempt record. The person
# decides (split the ticket, approve one more replan, or drop scope); SDLC_REPLAN_APPROVED="<who: why>" proceeds and
# appends "replan approved: planner run <n+1>: <who: why>" once to the task's skips.md after every gate passes
# (not on a dry run). dispatch.py
# prepare --approved is the Claude twin.
# Link check (T-0379): before a builder or verifier run on a step handoff (step-<n>/handoff.md), run.sh runs steps.py
# lint on the step dir; a cited .sdlc path that does not exist, or a report of the step's own prior attempt that does not
# name its step-<n>.superseded-<k> folder, prints the finding and exits 2 before any attempt record (dry runs too).
# Spec gate: before a plan-reviewer run (dry runs too, never in the run_lifecycle.py child, either
# backend), run.sh runs scripts/specgate.py check on the handoff dir. A refusal prints specgate's
# lines and "run.sh: specgate.py check refused the plan in <dir>; replan, or set SDLC_SPECGATE=off"
# on stderr and exits 2 before the lifecycle starts, so no attempt record, .running file, or
# runs.jsonl line exists. A pass or a skip prints nothing.
# Budget gate: before launching a role (dry runs too, never in the run_lifecycle.py child), run.sh runs
# budget.py status on the handoff. Exit 3 (warn or over) prints "run.sh: budget <pct>%: ask the user;
# budget.py ack" on stderr and exits 4 before any attempt record, .running file, or runs.jsonl line;
# any other exit (no budget, a crash) launches unchanged.
# Result pick: the run uses --output-format stream-json --verbose, because plain json keeps only the
# session's last result, and a background task notification arriving after the report ends the session
# with its own result ("origin":{"kind":"task-notification"}), losing the report. The log is parsed
# leniently (lines that are not JSON are skipped) and only "type":"result" events count. The saved
# event is the last one whose .result holds a line exactly the role's required heading (trailing
# whitespace ignored), else the last one whose .origin.kind is not task-notification, else the last
# one. It must have is_error false and a non-empty .result (else exit 1); its .result is written to
# the result file. The runs.jsonl cost, duration, and turns come from the last result event, which
# holds the session totals.
# Loaded context (T-0252): the runs.jsonl line always holds loaded_context, from `scripts/traces.py context
# <log> --backend <backend>` (traces/sources/context.py owns the rules): {"source":"stream-json","paths":[...]}
# with the file_path of every Read tool_use in the Claude log, {"source":"rollout","paths":[...]} with the files
# the Codex rollout's shell reads (cat, head, tail, sed, nl, less, more, bat) opened, or {"status": ...}
# ("log absent", "log unreadable", "rollout absent", "exec ephemeral: no rollout written", "rollout unreadable", "collector failed") when the list
# cannot be built; a status also prints one stderr line "run.sh: loaded context not recorded: <status>; see <log>".
# An empty paths list means the run read nothing through those channels. Entry files the host injects into the
# session are not in the log, so they are not listed. It never changes the exit code.
# Env: SDLC_DRY_RUN=1 prints the command only (after the preflight and .nvmrc resolution).
# SDLC_SPECGATE=off skips the spec gate with one stderr line "run.sh: SDLC_SPECGATE=off: spec gate
# skipped", and the plan-reviewer run's runs.jsonl line gets "specgate":"off".
# Bash timeouts: a real run passes BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS of 3600000 (as
# bench.sh does), keeping an inherited value only when it is a plain integer of at least 3600000.
# Claude Code moves a foreground Bash call to the background once it passes its timeout, and no
# PreToolUse hook sees that move, so hooks/block-background.sh cannot stop it (T-0105).
# Build base: a real run (never a dry run) of builder or verifier resolves the commit the step's
# build started from and stores it in <handoff dir>/base-sha (the handoff dir is the step dir). The
# base is, in this order (T-0381): (1) a base the handoff names, a line `base: <sha>` in handoff.md, which must
# be a commit that is an ancestor of HEAD or the run stops with exit 2 and `run.sh: SDLC_BASE_SHA refused: ...`;
# else (2) the sha recorded at the step's first dispatch, the first line of base-sha, valid when it names a commit
# that is an ancestor of HEAD, so a rework keeps its original base; when git rev-list --first-parent --merges
# <stored>..HEAD is non-empty, base = its first line (the newest resync merge on the first-parent chain), since
# builders commit only on merge steps and any other commit since the base is the step's own work; else (3)
# HEAD of the execution tree. Never the main checkout's HEAD. A missing or invalid record (junk, or a sha no
# longer an ancestor after a reset or rewrite) falls to HEAD. The execution tree is the handoff's own tree,
# except a handoff in the main checkout run from inside an owned linked (lane) worktree of the same repo,
# where it is that lane worktree. In a lane worktree a recorded sha that does not descend from the lane's
# fork point (git merge-base HEAD <main checkout HEAD>, or SDLC_BASE_REF) is stale and replaced by HEAD
# (T-0376). A caller-supplied SDLC_BASE_SHA is never used in place of that pick: one that resolves to a
# different commit is refused with the stderr line `run.sh: SDLC_BASE_SHA refused: ...` and the pick kept;
# the handoff names a different base only through its `base:` line. run.sh prints `base <sha>: <why>` on
# stderr. base-sha is written when it was missing or changed. The role gets SDLC_BASE_SHA=<base> next to
# SDLC_ROLE, so scope criteria can diff against the tree the build started from whether or not anything is
# committed later. Every other role gets SDLC_BASE_SHA removed from its env (even when the caller
# exported it) and writes no base-sha. Caveat: on a merge step the builder's own merge commit moves
# the base on the verifier run, so merge-step criteria use HEAD^1 instead.
# Mailbox notice: before launching a role (dry runs too, never in the run_lifecycle.py child), run.sh
# adds messages.py count --receiver for the role name and for the backend name (claude or codex). When
# the sum is above 0 it prints one stderr line "run.sh: <n> new message(s) for <role>; read with
# messages.py". A failed count adds 0. It never prints a body and never changes the exit code.
# Self-edit: bash reads a script from disk as it runs it, so a role that rewrites run.sh in place
# (a builder editing this file) would move the running process to its old byte offset in the new
# text, and a shorter file ends the run at EOF with status 0 and no result. Everything after
# set -euo pipefail is one { ... } group ending in an explicit exit: bash parses the whole group
# before running any of it and never reads the file again, so the running process keeps its
# behavior and still saves its result. Keep new code inside the group.
set -euo pipefail
{

role="${1:-}"; level="${2:-}"; handoff="${3:-}"
backend="${SDLC_BACKEND:-claude}"
case "$backend" in claude|codex) ;; *) echo "unknown SDLC_BACKEND: $backend" >&2; exit 2 ;; esac
if [[ "$backend" == claude && "${SDLC_CLAUDE_EXEC:-}" != 1 ]]; then
  echo "run.sh no longer runs Claude roles headless: use 'dispatch.py prepare $role $level <handoff>' and spawn the sub-agent (SDLC_CLAUDE_EXEC=1 is the legacy path for bench and CI)" >&2; exit 2
fi
usage() { echo "usage: run.sh <role> <level> <handoff.md>  (see levels in this file)" >&2; exit 2; }

# role:level -> model effort. Mirrors adapters/claude/levels.json (the table home) until this Claude branch is retired; keep in sync with it and skills/level-rubric/SKILL.md (Claude mapping).
case "$role:$level" in
  builder:L1)       model=opus;   effort=low ;;
  builder:L2)       model=sonnet; effort=high ;;
  builder:L3)       model=opus;   effort=medium ;;
  builder:L4)       model=opus;   effort=high ;;
  builder:L5)       model=opus;   effort=xhigh ;;
  planner:L1)       model=sonnet; effort=high ;;
  planner:L2)       model=opus;   effort=medium ;;
  planner:L3)       model=opus;   effort=high ;;
  verifier:L1)      model=opus;   effort=low ;;
  verifier:L2)      model=sonnet; effort=high ;;
  verifier:L3)      model=fable;  effort=xhigh ;;
  researcher:L1)    model=sonnet; effort=high ;;
  researcher:L2)    model=opus;   effort=medium ;;
  researcher:L3)    model=opus;   effort=high ;;
  architect:L1)     model=opus;   effort=xhigh ;;
  scout:L1)         model=sonnet; effort=low ;;
  archaeologist:L1) model=sonnet; effort=medium ;;
  filer:L1)         model=sonnet; effort=low ;;
  plan-reviewer:L1) model=fable;  effort=high ;;
  ui-designer:L1)   model=opus;   effort=high ;;
  *) usage ;;
esac
[[ -f "$handoff" ]] || { echo "handoff not found: $handoff" >&2; exit 2; }
# Git preflight: roles need a repo with a commit (diffs, worktrees). Never init git here.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo: run git init and commit first" >&2; exit 2; }
git rev-parse --verify -q HEAD >/dev/null || { echo "git repo has no commit: commit first" >&2; exit 2; }

# Node version: honor the repo's .nvmrc without sourcing or running nvm. Resolve it against
# installed dirs under ${NVM_DIR:-$HOME/.nvm}/versions/node and prepend that bin dir to PATH.
# One stderr line per outcome; never changes the exit code. No .nvmrc: nothing.
nvmrc="$(git rev-parse --show-toplevel)/.nvmrc"
if [[ -f "$nvmrc" ]]; then
  nvmrc_raw=$(tr -d '[:space:]' <"$nvmrc" || true)
  nvm_node="${NVM_DIR:-$HOME/.nvm}/versions/node"
  nvm_pick=""
  if [[ -z "$nvmrc_raw" ]]; then
    :
  elif [[ "$nvmrc_raw" =~ ^v?[0-9]+(\.[0-9]+)?(\.[0-9]+)?$ ]]; then
    nvm_want="${nvmrc_raw#v}"
    if [[ "$nvm_want" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      # Exact version: that dir only.
      [[ -d "$nvm_node/v$nvm_want" ]] && nvm_pick="v$nvm_want"
    else
      # Partial version: whole-component prefix match, highest by numeric compare.
      IFS=. read -r nw1 nw2 _ <<<"$nvm_want"
      best1=-1; best2=-1; best3=-1
      for d in "$nvm_node"/v*; do
        [[ -d "$d" ]] || continue
        [[ "${d##*/}" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]] || continue
        c1=$((10#${BASH_REMATCH[1]})); c2=$((10#${BASH_REMATCH[2]})); c3=$((10#${BASH_REMATCH[3]}))
        [[ "$c1" == "$((10#$nw1))" ]] || continue
        [[ -z "${nw2:-}" || "$c2" == "$((10#$nw2))" ]] || continue
        if (( c1 > best1 || (c1 == best1 && (c2 > best2 || (c2 == best2 && c3 > best3))) )); then
          best1=$c1; best2=$c2; best3=$c3; nvm_pick="${d##*/}"
        fi
      done
    fi
    if [[ -n "$nvm_pick" ]]; then
      nvm_bin="$nvm_node/$nvm_pick/bin"
      echo "run.sh: .nvmrc $nvmrc_raw: prepended $nvm_bin to PATH" >&2
      export PATH="$nvm_bin:$PATH"
    else
      echo "run.sh: .nvmrc $nvmrc_raw: not found under $nvm_node, PATH unchanged" >&2
    fi
  else
    echo "run.sh: .nvmrc $nvmrc_raw: alias not resolved, PATH unchanged" >&2
  fi
fi

plugin_root="$(cd "$(dirname "$0")/.." && pwd)"
handoff="$(cd "$(dirname "$handoff")" && pwd)/$(basename "$handoff")"
# hdir is the handoff dir (the handoff gates read it); dir is its records dir (scripts/records.sh, the
# scripts/order.py records_dir rule), where everything this run writes or numbers goes. skips.md stays in the
# task folder (order.py task-dir).
hdir="$(dirname "$handoff")"
# shellcheck source=records.sh
. "$plugin_root/scripts/records.sh"
# A dry run only names it; a real run makes it (records_dir_make) once every gate has passed, before the lifecycle owner.
dir="$(records_dir "$hdir")"
# T-0593: a plugin_min: line in .sdlc/config above this plugin's own manifest version stops the run (exit 2, one line
# naming both versions and the host's update command); no line, no check.
python3 "$plugin_root/scripts/plugin_min.py" check "$hdir" --host "$backend" || exit 2
# Never overwrite an earlier result: the first run is <role>-<level>, later ones <role>-<level>-<k>.
name="${SDLC_ATTEMPT_NAME:-$role-$level}"
if [[ -z "${SDLC_ATTEMPT_NAME:-}" && ( -e "$dir/$name.md" || -e "$dir/$name.request.json" ) ]]; then
  k=2
  while [[ -e "$dir/$role-$level-$k.md" || -e "$dir/$role-$level-$k.request.json" ]]; do k=$((k + 1)); done
  name="$role-$level-$k"
fi
result="$dir/$name.md"
log="$dir/$name.log"

# A verifier never runs on the build's model family (T-0005, user decision 2026-09-24):
# Fable or Sonnet build -> Opus at the same effort; an Opus build -> Sonnet at the same effort (T-0519).
if [[ "$backend" == claude && "$role" == verifier ]]; then
  built=$(python3 "$plugin_root/scripts/order.py" newest "$dir" builder 2>/dev/null || true)
  # No build in the handoff dir (a verifier launched at the task dir): take the newest build of the
  # highest-numbered live step-<n>/ under it that holds one; step-<n>.superseded-<k>/ never matches.
  # scripts/codex_roles.py resolve is the Codex twin of this rule.
  if [[ -z "$built" ]]; then
    best_n=-1
    for sd in "$dir"/step-*; do
      [[ -d "$sd" ]] || continue
      sn="${sd##*/}"
      [[ "$sn" =~ ^step-[0-9]+$ ]] || continue
      sn="${sn#step-}"
      (( 10#$sn > best_n )) || continue
      sb=$(python3 "$plugin_root/scripts/order.py" newest "$sd" builder 2>/dev/null || true)
      [[ -n "$sb" ]] || continue
      best_n=$((10#$sn)); built="$sb"
    done
  fi
  bmodel=""
  if [[ -n "$built" ]]; then
    bmodel=$(grep -o 'model=[a-z]*' "$built" | head -1 | cut -d= -f2 || true)
  else
    # A solo ticket has no builder result either: the newest `role solo` record in runs.jsonl holds the
    # family (T-0356; dispatch.py solo_model is the twin), so a Sonnet solo's L2 verifier moves to Opus.
    bmodel=$(python3 - "$plugin_root/scripts" "$dir" 2>/dev/null <<'PY' || true
import sys
sys.path.insert(0, sys.argv[1])
import order
got = [r.get('model') for _, r in order.records(sys.argv[2]) if r.get('role') == 'solo']
print(got[-1] if got and isinstance(got[-1], str) else '')
PY
)
  fi
  if [[ -n "$bmodel" && "$model" == "$bmodel" ]]; then
    case "$model" in
      fable|sonnet) model=opus ;;
      opus) model=sonnet ;;
    esac
  fi
fi
# A plan-reviewer never runs on the planner's model family (T-0171, user decision 2026-09-30):
# an Opus planner -> Fable, a Fable planner -> Opus, at the same effort; a Sonnet planner, or none, keeps the row (Fable high, T-0519).
if [[ "$backend" == claude && "$role" == plan-reviewer ]]; then
  planned=$(python3 "$plugin_root/scripts/order.py" newest "$dir" planner 2>/dev/null || true)
  if [[ -n "$planned" ]]; then
    pmodel=$(grep -o 'model=[a-z]*' "$planned" | head -1 | cut -d= -f2 || true)
    if [[ "$model" == "$pmodel" && "$model" == opus ]]; then
      model=fable
    elif [[ "$model" == "$pmodel" && "$model" == fable ]]; then
      model=opus
    fi
  fi
fi

# Codex: a verifier, or a plan-reviewer, whose model equals the model it reviews (the newest
# builder's, or the newest planner's) switches to a configured alternate, or else shares that
# model; resolve then prints a third token "shared" (T-0163, T-0171).
shared=""
if [[ "$backend" == codex ]]; then
  # A dry run of a new task has no records dir yet: resolve reads the handoff dir (order.py maps it the same way).
  rdir="$dir"; [[ -d "$rdir" ]] || rdir="$hdir"
  resolved=$(python3 "$plugin_root/scripts/codex_roles.py" resolve "$role" "$level" "$rdir") || exit 2
  read -r model effort shared <<<"$resolved"
fi
shared_with_builder=false; shared_note=""
if [[ "$shared" == shared ]]; then shared_with_builder=true; shared_note=" shared_with_builder=yes"; fi

# Mailbox notice (see the header): new messages for the role and the backend; parent process only.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 ]]; then
  msg_total=0
  for msg_name in "$role" "$backend"; do
    if msg_n=$(python3 "$plugin_root/scripts/messages.py" count --receiver "$msg_name" 2>/dev/null) && [[ "$msg_n" =~ ^[0-9]+$ ]]; then
      msg_total=$((msg_total + msg_n))
    fi
  done
  if (( msg_total > 0 )); then
    echo "run.sh: $msg_total new message(s) for $role; read with messages.py" >&2
  fi
fi

# Goal precheck (T-0261): a planner or plan-reviewer on a task handoff (<task dir>/handoff.md, not a step
# dir) needs the ## Goal section steps.py split reads; refuse before any attempt record, dry runs too.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 && ( "$role" == planner || "$role" == plan-reviewer ) \
      && "$(basename "$handoff")" == handoff.md && "$(basename "$hdir")" != step-* ]]; then
  if ! goal_out=$(python3 "$plugin_root/scripts/steps.py" precheck "$hdir" 2>&1); then
    printf '%s\n' "$goal_out" >&2
    echo "run.sh: steps.py precheck refused the task handoff in $hdir; add a ## Goal section" >&2
    exit 2
  fi
fi

# Replan cap (see the header): a third planner run on a task needs the person's approval; dry runs too.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 && "$role" == planner ]]; then
  planner_n=0
  if [[ -d "$dir" ]]; then planner_n=$(find "$dir" -maxdepth 1 -type f -name 'planner-L*.md' | wc -l | tr -d ' '); fi
  if (( planner_n >= 2 )); then
    replan_ok=$(printf '%s' "${SDLC_REPLAN_APPROVED:-}" | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')
    if [[ -z "$replan_ok" ]]; then
      echo "run.sh: replan cap: $dir already holds $planner_n planner results (the first plan and the one replan); planner run $((planner_n + 1)) needs the person's approval" >&2
      echo "run.sh: replan cap: ask the person (split the ticket, approve one more replan, or drop scope), then rerun with SDLC_REPLAN_APPROVED=\"<who: why>\"" >&2
      exit 2
    fi
    if ! [[ "$replan_ok" =~ ^[^:]*[^[:space:]:][^:]*:[[:space:]]*[^[:space:]] ]]; then
      echo "run.sh: replan cap: SDLC_REPLAN_APPROVED takes \"<who: why>\": who approved, a colon, and why" >&2
      exit 2
    fi
    replan_line="replan approved: planner run $((planner_n + 1)): $replan_ok"
  fi
fi

# Link check (T-0379): a builder or verifier on a step handoff (<task dir>/step-<n>/handoff.md) needs every cited
# .sdlc path to exist and every report of the step's own prior attempt to name its step-<n>.superseded-<k> folder
# (steps.py lint); refuse before any attempt record, dry runs too.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 && ( "$role" == builder || "$role" == verifier ) \
      && "$(basename "$handoff")" == handoff.md && "$(basename "$hdir")" =~ ^step-[0-9]+$ ]]; then
  if ! links_out=$(python3 "$plugin_root/scripts/steps.py" lint "$hdir" 2>&1); then
    printf '%s\n' "$links_out" >&2
    echo "run.sh: steps.py lint refused the links in $handoff; fix the cited paths (rewrite them to the step-<n>.superseded-<k> folder) before dispatching" >&2
    exit 2
  fi
fi

# Lane gate (see the header): solo is the path of least resistance; a planner, builder, or plan-reviewer on a
# solo-lane ticket needs SDLC_LANE_OVERRIDE. Parent process only, dry runs too.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 && ( "$role" == planner || "$role" == builder || "$role" == plan-reviewer ) ]]; then
  lane_dir="$(python3 "$plugin_root/scripts/order.py" task-dir "$hdir" 2>/dev/null || true)"
  if [[ -n "$lane_dir" && -f "$lane_dir/handoff.md" ]] && grep -Eq '^id: *T-[0-9]+' "$lane_dir/handoff.md" \
     && ! { [[ -f "$lane_dir/skips.md" ]] && grep -Ei '^(- )?lane: ' "$lane_dir/skips.md" | tail -n 1 | grep -Eviq '^(- )?lane: *solo'; } \
     && [[ "$(python3 "$plugin_root/scripts/steps.py" lane --check "$lane_dir" 2>/dev/null | head -n 1)" == solo ]]; then
    if [[ -n "${SDLC_LANE_OVERRIDE:-}" ]]; then
      export SDLC_LANE_OVERRIDE_APPLIED="$SDLC_LANE_OVERRIDE"
      lane_line="lane override: $SDLC_LANE_OVERRIDE"
      [[ "${SDLC_DRY_RUN:-}" == 1 ]] || grep -qxF "$lane_line" "$lane_dir/skips.md" 2>/dev/null || printf '%s\n' "$lane_line" >>"$lane_dir/skips.md"
    else
      # The solo level is the ticket size as a level; a deprecated alias size (S, M) reads as L1, L2.
      lane_size=$(sed -n 's/^size: *\([A-Z0-9]*\).*/\1/p' "$lane_dir/handoff.md" | head -n 1)
      case "$lane_size" in S) lane_size=L1 ;; M) lane_size=L2 ;; L1|L2|L3) ;; *) lane_size=L2 ;; esac
      echo "run.sh: lane solo for $lane_dir: use the solo agent: python3 $plugin_root/scripts/solo_run.py run --task-dir $lane_dir --tier $lane_size --brief \"<brief>\"" >&2
      echo "run.sh: or set SDLC_LANE_OVERRIDE=\"<reason the chain is needed>\" to run $role anyway (recorded in skips.md)" >&2
      exit 5
    fi
  fi
fi

# Spec gate (see the header): plan-reviewer only, parent process only, dry runs too.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 && "$role" == plan-reviewer ]]; then
  if [[ "${SDLC_SPECGATE:-}" == off ]]; then
    echo "run.sh: SDLC_SPECGATE=off: spec gate skipped" >&2
  elif ! specgate_out=$(python3 "$plugin_root/scripts/specgate.py" check "$hdir" 2>&1); then
    [[ -z "$specgate_out" ]] || printf '%s\n' "$specgate_out" >&2
    echo "run.sh: specgate.py check refused the plan in $hdir; replan, or set SDLC_SPECGATE=off" >&2
    exit 2
  fi
fi

# Budget gate (see the header): a ticket at 80 percent of its budget with no ack stops before launch.
if [[ "${SDLC_LIFECYCLE_CHILD:-}" != 1 ]]; then
  budget_rc=0
  budget_out=$(python3 "$plugin_root/scripts/budget.py" status "$handoff" 2>/dev/null) || budget_rc=$?
  if [[ "$budget_rc" == 3 ]]; then
    budget_pct=$(sed -n 's/^percent: //p' <<<"$budget_out" | head -1)
    echo "run.sh: budget ${budget_pct}%: ask the user; budget.py ack" >&2
    exit 4
  fi
fi

# Shared lifecycle owner holds the directory lock across either backend.
if [[ "${SDLC_DRY_RUN:-}" != 1 && "${SDLC_LIFECYCLE_CHILD:-}" != 1 ]]; then
  records_dir_make "$hdir" >/dev/null || { echo "run.sh: cannot make the records dir $dir" >&2; exit 2; }
  if [[ -n "${replan_line:-}" ]]; then  # the replan cap approval, recorded once every gate has passed
    replan_skips="$(python3 "$plugin_root/scripts/order.py" task-dir "$hdir" 2>/dev/null || echo "$hdir")/skips.md"
    grep -qxF "$replan_line" "$replan_skips" 2>/dev/null || printf '%s\n' "$replan_line" >>"$replan_skips"
  fi
  exec python3 "$plugin_root/scripts/run_lifecycle.py" run "$role" "$level" "$handoff" "$backend" "$model" "$effort"
fi

# Skills declared in the agent's frontmatter (skills: list). `claude --agent` does not preload
# them (probed 2026-09-24), so append each skill body to the system prompt here.
agent_file="$plugin_root/agents/$role.md"
skills=$(awk '/^---$/{n++; next} n==1 && /^skills:/{f=1; next} n==1 && f && /^  - /{sub(/^  - /,""); print; next} n==1 && f{f=0}' "$agent_file")
skill_prompt=()
if [[ "$backend" == claude && -n "$skills" ]]; then
  skill_file=$(mktemp)
  # Removes it on a dry run or an early exit; on_exit replaces this trap and removes it too.
  trap 'rm -f "$skill_file"' EXIT
  while IFS= read -r sk; do
    src="$plugin_root/skills/$sk/SKILL.md"
    [[ -f "$src" ]] || { echo "agent $role declares missing skill: $sk" >&2; exit 2; }
    { echo "# Skill: $sk (loaded for this role; its relative paths are under $plugin_root/skills/$sk/)"
      # shellcheck disable=SC2016 # ${CLAUDE_PLUGIN_ROOT} is the literal text to replace.
      awk '/^---$/{n++; next} n>=2' "$src" | sed 's|${CLAUDE_PLUGIN_ROOT}|'"$plugin_root"'|g'
      echo; } >>"$skill_file"
  done <<<"$skills"
  skill_prompt=(--append-system-prompt-file "$skill_file")
fi

read_only=()
case "$role" in
  planner|verifier|plan-reviewer|researcher|architect|scout|archaeologist|filer)
    read_only=(--disallowedTools Edit Write NotebookEdit) ;;
esac

# Throwaway worktree prefix owned by this run (see the header). Not created here.
toplevel="$(git rev-parse --show-toplevel)"
# T-0550: the worktree root follows the main checkout (the parent of the common .git dir), never the current lane.
main_top=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || main_top=""
if [[ "${main_top##*/}" == .git ]]; then main_top="${main_top%/.git}"; else main_top="$toplevel"; fi
# T-0563: wtroot.py root is the sibling <main checkout>.worktrees; it also honors a worktree_root: config line and a
# bare clone's <bare parent>/lanes (T-0561).
wt_root=$(python3 "$plugin_root/scripts/wtroot.py" root 2>/dev/null) || wt_root=""
[[ -n "$wt_root" ]] || wt_root="$main_top.worktrees"
wt_tmp="$wt_root/tmp/$role-$$"

cmd=(claude -p
  --plugin-dir "$plugin_root"
  --agent "sdlc:$role"
  --model "$model" --effort "$effort"
  --dangerously-skip-permissions
  --output-format stream-json --verbose
  ${read_only[@]+"${read_only[@]}"}
  ${skill_prompt[@]+"${skill_prompt[@]}"}
  --
  "Handoff: $handoff
Artifacts dir: $dir
Throwaway worktrees only under $wt_tmp (git worktree add --detach \"$wt_tmp/<name>\" HEAD); write that path literally.
Your final message is saved verbatim as $result. Make it exactly the output format your instructions define: start with its first heading, with nothing before it and nothing after the last section.")

if [[ "$backend" == codex ]]; then
  cmd=(python3 "$plugin_root/scripts/codex_exec.py" "$role" "$level"
    "Handoff: $handoff
Artifacts dir: $dir
Throwaway worktrees only under $wt_tmp (git worktree add --detach \"$wt_tmp/<name>\" HEAD); write that path literally.
Your final message is saved verbatim as $result. Use exactly the sections in your role contract."
    --model "$model" --effort "$effort" --request-file "$dir/$name.request.json")
fi

if [[ "${SDLC_DRY_RUN:-}" == 1 ]]; then printf '%q ' "${cmd[@]}"; echo; exit 0; fi

# Build base (see the header): builder and verifier only; every other role gets no SDLC_BASE_SHA.
supplied="${SDLC_BASE_SHA:-}"
unset SDLC_BASE_SHA
base_env=()
if [[ "$role" == builder || "$role" == verifier ]]; then
  stored=""
  [[ -f "$dir/base-sha" ]] && { IFS= read -r stored <"$dir/base-sha" || true; }
  stored="${stored//[[:space:]]/}"
  supplied="${supplied//[[:space:]]/}"
  base=""
  # T-0376/T-0381: git runs in the execution tree. That is the handoff's own tree, except a handoff in the
  # main checkout run from inside an owned lane worktree (the shared-handoff shape), where it is that lane.
  xt="$hdir"
  gd=$(cd "$hdir" && cd "$(git rev-parse --git-dir 2>/dev/null)" 2>/dev/null && pwd -P || true)
  gc=$(cd "$hdir" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P || true)
  if [[ -n "$gd" && "$gd" == "$gc" ]]; then
    ct=$(git rev-parse --show-toplevel 2>/dev/null || true)
    if [[ -n "$ct" ]]; then
      cgd=$(cd "$ct" && cd "$(git rev-parse --git-dir 2>/dev/null)" 2>/dev/null && pwd -P || true)
      cgc=$(cd "$ct" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P || true)
      if [[ -n "$cgd" && "$cgd" != "$cgc" && "$cgc" == "$gc" ]]; then xt="$ct"; gd="$cgd"; gc="$cgc"; fi
    fi
  fi
  # In a linked (lane) worktree a recorded sha older than the lane's fork point (merge-base of HEAD and the main
  # checkout HEAD, or SDLC_BASE_REF) is stale.
  floor=""
  if [[ -n "$gd" && "$gd" != "$gc" ]]; then
    fref="${SDLC_BASE_REF:-}"
    [[ -n "$fref" ]] || fref=$(git -C "$xt" worktree list --porcelain | sed -n 's/^HEAD //p' | head -1)
    [[ -z "$fref" ]] || floor=$(git -C "$xt" merge-base HEAD "$fref" 2>/dev/null || true)
  fi
  # T-0381: the base of a step is, in this order, (1) a base the handoff names (a line `base: <sha>`), else (2) the
  # sha recorded at the step's first dispatch (base-sha, kept valid), else (3) HEAD of the execution tree. Never the
  # main checkout's HEAD. A named base that is not an ancestor of the execution HEAD stops the run.
  why=""
  named=$(sed -nE 's/^[[:space:]]*(-[[:space:]]+)?[Bb]ase:[[:space:]]*([0-9a-fA-F]{7,40})[[:space:]]*(#.*)?$/\2/p' "$handoff" | head -1)
  if [[ -n "$named" ]]; then
    if git -C "$xt" rev-parse -q --verify "$named^{commit}" >/dev/null 2>&1 \
      && git -C "$xt" merge-base --is-ancestor "$named" HEAD >/dev/null 2>&1; then
      base=$(git -C "$xt" rev-parse "$named^{commit}"); why="named in the handoff"
    else
      echo "run.sh: SDLC_BASE_SHA refused: $handoff names base $named, which is not a commit that is an ancestor of HEAD in $xt" >&2
      exit 2
    fi
  fi
  if [[ -z "$base" && -n "$stored" ]] && git -C "$xt" rev-parse -q --verify "$stored^{commit}" >/dev/null 2>&1 \
    && git -C "$xt" merge-base --is-ancestor "$stored" HEAD >/dev/null 2>&1 \
    && { [[ -z "$floor" ]] || git -C "$xt" merge-base --is-ancestor "$floor" "$stored" >/dev/null 2>&1; }; then
    base=$(git -C "$xt" rev-parse "$stored^{commit}"); why="recorded at the first dispatch (base-sha)"
    resync=$(git -C "$xt" rev-list --first-parent --merges "$base..HEAD" | head -1 || true)
    [[ -z "$resync" ]] || { base="$resync"; why="newest resync merge since the recorded base-sha"; }
  fi
  [[ -n "$base" ]] || { base=$(git -C "$xt" rev-parse HEAD); why="HEAD of the execution tree (nothing named or recorded)"; }
  # A supplied SDLC_BASE_SHA is checked against that pick; it never replaces it.
  if [[ -n "$supplied" ]]; then
    sup=$(git -C "$xt" rev-parse -q --verify "$supplied^{commit}" 2>/dev/null || true)
    if [[ "$sup" != "$base" ]]; then
      echo "run.sh: SDLC_BASE_SHA refused: $supplied (supplied) differs from the step base ${base:0:12} ($why); name it in the handoff with a line 'base: <sha>' to use it" >&2
    fi
  fi
  [[ "$base" == "$stored" ]] || printf '%s\n' "$base" >"$dir/base-sha"
  echo "run.sh: base ${base:0:12}: $why${floor:+; lane fork point ${floor:0:12}}" >&2
  base_env=("SDLC_BASE_SHA=$base")
fi

# phys <path>: physical path, resolving the deepest existing ancestor, so a missing path still compares.
phys() {
  local p="$1" rest="" r
  while [[ "$p" == /?* && ! -d "$p" ]]; do rest="/${p##*/}$rest"; p="${p%/*}"; done
  r=$(cd "${p:-/}" 2>/dev/null && pwd -P) || { printf '%s\n' "$1"; return 0; }
  printf '%s%s\n' "${r%/}" "$rest"
}
# Reaps dead-owner prefixes under <worktree root>/tmp and the legacy tmp dirs, never this run's own (see the header). Never fails.
reap_tmp() {
  bash "$plugin_root/scripts/reap-tmp-worktrees.sh" "$main_top" "$wt_tmp" >/dev/null 2>&1 || :
}
# Removes every worktree under this run's prefix only. Runs without errexit; never fails.
cleanup_worktrees() {
  local wt_real line p pr
  wt_real=$(phys "$wt_tmp")
  while IFS= read -r line; do
    case "$line" in "worktree "*) p="${line#worktree }" ;; *) continue ;; esac
    pr=$(phys "$p")
    if [[ "$pr" == "$wt_real" || "$pr" == "$wt_real"/* || "$p" == "$wt_tmp" || "$p" == "$wt_tmp"/* ]]; then
      git -C "$toplevel" worktree remove --force --force "$p" >/dev/null 2>&1
    fi
  done < <(git -C "$toplevel" worktree list --porcelain 2>/dev/null)
  rm -rf "$wt_tmp"
  reap_tmp
  git -C "$toplevel" worktree prune >/dev/null 2>&1
  rmdir "$wt_root/tmp" >/dev/null 2>&1
  return 0
}
reap_tmp
# Stray report baseline (see the header): worktree paths and local branches before the role runs.
snap_wt=$(git -C "$toplevel" worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p') || snap_wt=""
snap_br=$(git -C "$toplevel" for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null) || snap_br=""
stray_done=0; stray_reported=0
stray_wt=(); stray_wt_br=(); stray_br=()
# in_list <item> <newline-separated list>: exact line match.
in_list() {
  local x
  while IFS= read -r x; do [[ "$x" == "$1" ]] && return 0; done <<<"$2"
  return 1
}
# Fills stray_wt (paths), stray_wt_br (branch or "" per path), and stray_br once per run.
# Scope rule, the same as dispatch.py strays (T-0371, T-0391): a stray belongs to this role only when it
# is a worktree under <worktree root>/tmp (this run's own prefix left out) or on a branch whose name
# starts with this run's prefix name ($role-$$), or a branch with that name as prefix. Sibling lanes and
# peers elsewhere are not reported. Keep the two in step.
# Called in an || list, so it runs without errexit; never fails.
detect_strays() {
  (( stray_done )) && return 0
  stray_done=1
  local wt_real line p="" b="" pr br now_wt now_br mine tmp_root
  wt_real=$(phys "$wt_tmp")
  mine="${wt_tmp##*/}"; tmp_root=$(phys "$wt_root/tmp")
  now_wt=$(git -C "$toplevel" worktree list --porcelain 2>/dev/null)
  # Porcelain records end at a blank line; $(...) strips the last one, so the input adds it back.
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) p="${line#worktree }"; b="" ;;
      "branch "*) b="${line#branch }"; b="${b#refs/heads/}" ;;
      "")
        if [[ -n "$p" ]] && ! in_list "$p" "$snap_wt"; then
          pr=$(phys "$p")
          if ! [[ "$pr" == "$wt_real" || "$pr" == "$wt_real"/* || "$p" == "$wt_tmp" || "$p" == "$wt_tmp"/* ]]; then
            if [[ "$pr" == "$tmp_root"/* || ( -n "$b" && "$b" == "$mine"* ) ]]; then
              stray_wt+=("$p"); stray_wt_br+=("$b")
            fi
          fi
        fi
        p=""; b="" ;;
    esac
  done <<<"$now_wt"$'\n'
  now_br=$(git -C "$toplevel" for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null)
  while IFS= read -r br; do
    [[ -n "$br" && "$br" == "$mine"* ]] && ! in_list "$br" "$snap_br" && stray_br+=("$br")
  done <<<"$now_br"
  return 0
}
# json_array <item>...: a compact JSON array of strings.
json_array() {
  if (( $# == 0 )); then echo '[]'; return 0; fi
  printf '%s\n' "$@" | jq -Rsc 'split("\n") | .[:-1]'
}
# Prints the stray lines on stderr, once per run.
report_strays() {
  (( stray_reported )) && return 0
  stray_reported=1
  local i
  for (( i = 0; i < ${#stray_wt[@]}; i++ )); do
    echo "run.sh: stray worktree appeared during this run: ${stray_wt[$i]}${stray_wt_br[$i]:+ [${stray_wt_br[$i]}]}" >&2
  done
  for (( i = 0; i < ${#stray_br[@]}; i++ )); do
    echo "run.sh: stray branch appeared during this run: ${stray_br[$i]}" >&2
  done
  return 0
}
# Stops a role still running (TERM, up to 2 s, then KILL) so it cannot recreate files during cleanup.
stop_role() {
  local i
  [[ -n "$role_pid" ]] && kill -0 "$role_pid" 2>/dev/null || return 0
  kill -TERM "$role_pid" 2>/dev/null
  for (( i = 0; i < 20; i++ )); do kill -0 "$role_pid" 2>/dev/null || break; sleep 0.1; done
  kill -0 "$role_pid" 2>/dev/null && kill -KILL "$role_pid" 2>/dev/null
  wait "$role_pid" 2>/dev/null
  role_pid=""
  return 0
}
on_exit() {
  local rc=$?
  set +e
  stop_role
  rm -f "$running" ${skill_file:+"$skill_file"}
  cleanup_worktrees
  detect_strays || :
  report_strays
  exit "$rc"
}
# limit_marker: on a failed run, a 429 or session limit in the log leaves a resume marker and prints the command.
limit_marker() {
  local ev resume reset hint
  ev=$(grep -Eim1 '429|session limit|usage limit|hit your (session |usage )?limit|rate.?limit' "$log" 2>/dev/null | cut -c1-200) || return 0
  [[ -n "$ev" ]] || return 0
  resume="bash $plugin_root/scripts/run.sh $role $level $handoff"
  # reset time (T-0298): the text after "resets" (for example 1:40pm), absent when the log has none
  reset=$(grep -Eio -m1 'resets +[0-9]{1,2}(:[0-9]{2})? *[ap]m' "$log" 2>/dev/null | head -1 | sed -E 's/^resets +//I') || reset=""
  jq -nc --arg role "$role" --arg level "$level" --arg handoff "$handoff" --arg resume "$resume" --arg ev "$ev" --arg reset "$reset" \
    '{ts: (now|todate), role: $role, level: $level, handoff: $handoff, resume: $resume, evidence: $ev} + (if $reset != "" then {reset: $reset} else {} end)' \
    >"$dir/$role-$level.limit" 2>/dev/null || :
  hint="run.sh: session limit: resume with: $resume"
  [[ -z "$reset" ]] || hint="$hint (resets $reset)"
  echo "$hint" >&2
  return 0
}
running="$dir/$role-$level.running"
date +%s >"$running"
role_pid=""
trap on_exit EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
# Bash timeouts (see the header, T-0105): at least 3600000 ms, else replaced.
bash_timeout() { if [[ "${1:-}" =~ ^[0-9]+$ ]] && (( 10#$1 >= 3600000 )); then echo "$1"; else echo 3600000; fi; }
bash_default_ms=$(bash_timeout "${BASH_DEFAULT_TIMEOUT_MS:-}")
bash_max_ms=$(bash_timeout "${BASH_MAX_TIMEOUT_MS:-}")
# The role runs in the background and run.sh waits for it, because bash defers a trap until a
# foreground child exits; wait returns at once on INT, TERM, or HUP, so on_exit runs promptly.
env -u SDLC_LIFECYCLE_CHILD -u SDLC_ATTEMPT_NAME ${base_env[@]+"${base_env[@]}"} SDLC_ROLE="$role" SDLC_TMP_WORKTREES="$wt_tmp" BASH_DEFAULT_TIMEOUT_MS="$bash_default_ms" BASH_MAX_TIMEOUT_MS="$bash_max_ms" "${cmd[@]}" </dev/null >"$log" 2>&1 &
role_pid=$!
role_rc=0
wait "$role_pid" || role_rc=$?
role_pid=""
(( role_rc == 0 )) || { echo "$role exited non-zero; see $log" >&2; limit_marker; exit 1; }
# Result pick (see the header): result events only, non-JSON lines skipped.
sect=$(python3 "$plugin_root/scripts/results.py" key "$role")
events=$(jq -R -c 'fromjson? // empty | select(type == "object" and .type == "result")' "$log" 2>/dev/null || true)
pick=$(jq -s -c --arg h "## $sect" '
  def has_head: (.result | strings | split("\n") | map(sub("[ \t\r]+$"; "")) | any(. == $h)) // false;
  (map(select(has_head)) | last)
  // (map(select((.origin.kind? // "") != "task-notification")) | last)
  // last // empty' <<<"$events" 2>/dev/null || true)
last_ev=$(jq -s -c 'last // empty' <<<"$events" 2>/dev/null || true)
if [[ -z "$pick" ]] || ! jq -e '.is_error == false and (.result | strings | length > 0)' <<<"$pick" >/dev/null 2>&1; then
  echo "$role returned no result; see $log" >&2; limit_marker; exit 1
fi
{ echo "<!-- role=$role level=$level model=$model effort=$effort$shared_note -->"; jq -r '.result' <<<"$pick"; } >"$result"
detect_strays || :
stray_wt_json=$(json_array ${stray_wt[@]+"${stray_wt[@]}"}) || stray_wt_json='[]'
stray_br_json=$(json_array ${stray_br[@]+"${stray_br[@]}"}) || stray_br_json='[]'
# Handoff freeze (warn mode): the lifecycle owner records the handoff's sha256 at launch in
# SDLC_HANDOFF_SHA256; a different hash now means the handoff changed while this role ran.
handoff_start_sha="${SDLC_HANDOFF_SHA256:-}"
stale_input=false
if [[ -n "$handoff_start_sha" ]]; then
  handoff_now_sha=$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$handoff" 2>/dev/null || true)
  [[ -n "$handoff_now_sha" && "$handoff_now_sha" != "$handoff_start_sha" ]] && stale_input=true
fi
specgate_flag=""
if [[ "$role" == plan-reviewer && "${SDLC_SPECGATE:-}" == off ]]; then specgate_flag=off; fi
# Loaded context (see the header, T-0252): traces.py context reads the run's log (or Codex rollout);
# a status instead of paths ('log absent', 'rollout absent') is reported on stderr, never recorded empty.
ctx_json=$(python3 "$plugin_root/scripts/traces.py" context "$log" --backend "$backend" 2>/dev/null) || ctx_json=""
jq -e 'type == "object" and (has("paths") or has("status"))' <<<"$ctx_json" >/dev/null 2>&1 || ctx_json='{"status":"collector failed"}'
ctx_status=$(jq -r '.status // empty' <<<"$ctx_json")
[[ -z "$ctx_status" ]] || echo "run.sh: loaded context not recorded: $ctx_status; see $log" >&2
jq -c --arg role "$role" --arg level "$level" --arg model "$model" --arg effort "$effort" \
  --arg handoff_sha256 "$handoff_start_sha" --argjson stale_input "$stale_input" \
  --arg attempt_id "${SDLC_ATTEMPT_ID:-}" --arg routing_reason "${SDLC_ROUTING_REASON:-}" \
  --arg backend "$backend" --arg file "$name.md" --argjson stray_wt "$stray_wt_json" --argjson stray_br "$stray_br_json" \
  --argjson shared_with_builder "$shared_with_builder" --arg specgate "$specgate_flag" \
  --arg lane_override "${SDLC_LANE_OVERRIDE_APPLIED:-}" --argjson loaded_context "$ctx_json" \
  '{ts: (now|todate), role: $role, level: $level, model: $model, effort: $effort, file: $file, shared_with_builder: $shared_with_builder,
    attempt_id: $attempt_id, handoff_sha256: $handoff_sha256, stale_input: $stale_input, routing_reason: $routing_reason, backend: $backend, transport: (.transport // $backend), usage: .usage, cost_usd: .total_cost_usd, duration_ms: .duration_ms, turns: .num_turns,
    stray_worktrees: $stray_wt, stray_branches: $stray_br, loaded_context: $loaded_context}
    + (if $specgate == "" then {} else {specgate: $specgate} end)
    + (if $lane_override == "" then {} else {lane_override: $lane_override} end)
    + (if has("profile_fingerprint") then {profile_fingerprint, profile_check} else {} end)' <<<"$last_ev" >>"$dir/runs.jsonl"

if [[ "$stale_input" == true ]]; then
  echo "run.sh: stale input: $handoff changed while $role ran" >&2
fi

# Result check (see the header): results.py prints one "results.py: <file>: <reason>" line on failure.
if ! chk=$(python3 "$plugin_root/scripts/results.py" validate "$result" --role "$role" 2>&1); then
  reason=${chk#"results.py: $result: "}
  echo "run.sh: $role result ${reason:-failed the result check}; see $result" >&2
  exit 3
fi
rm -f "$dir/$role-$level.limit"
# Red checkpoint (T-0378): a completed build without pre-edit (red) controls leaves a process deviation.
if [[ "$role" == builder ]]; then
  python3 "$plugin_root/scripts/redck.py" audit "$handoff" --attempt-id "${SDLC_ATTEMPT_ID:-}" >/dev/null || :
fi
echo "$result"
exit 0
}

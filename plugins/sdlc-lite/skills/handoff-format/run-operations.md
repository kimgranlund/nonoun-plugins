# Run readiness and recovery

Resolve the installed plugin root from the invoking skill. Run readiness before starting a workflow:

```sh
python3 "<plugin-root>/scripts/readiness.py" --backend claude --project "<project-root>"
python3 "<plugin-root>/scripts/readiness.py" --backend codex --transport subagent --project "<project-root>"
```

Use `--transport exec` for standalone Codex execution. These read-only checks inspect tools, Git baseline, plugin configuration, and Codex generated/project agents as applicable. They do not authenticate, spend a model call, or establish that an existing Codex chat loaded new agents. For native dispatch, confirm the exact named agent is available and that the host has delegation capacity. Fix reported setup issues before dispatch; do not widen permissions to pass a check. The shared role runner also performs local readiness checks.

Pass `dispatch.py prepare --routing-reason` (Codex `run.sh`: `SDLC_ROUTING_REASON`) per invocation to the reason for the selected role and level: user selection, task scope, or recorded escalation evidence. Keep the current model/effort mappings. Without a reason, the runner explicitly records that the caller supplied no task-specific rationale.

Every actual runner invocation reserves a unique `<role>-<level>[-N].attempt.json` before launching the backend. It captures the attempt ID, selected role/level/model/effort, backend/transport, reason, timestamps, and terminal exit status. Normal `runs.jsonl` rows carry the same ID and reason. A `completed` attempt means the runner accepted the report format and exited successfully; inspect the role's Status/Verdict for the actual work outcome. A failed or blocked verification is not task completion.

A handoff directory permits only one active pipeline run. Put roles that must run in parallel in separate handoff directories. A duplicate launch fails instead of overlapping a build and verification against the same handoff. Failed attempts and logs are never overwritten by retries.

```sh
python3 "<plugin-root>/scripts/run_lifecycle.py" status "<handoff-directory>"
python3 "<plugin-root>/scripts/run_lifecycle.py" recover "<handoff-directory>"
```

Status reads attempt records; `running` may be stale after a forced process kill. Recovery acquires the directory lock and refuses while a local runner still owns it. Once unlocked, it marks unfinished attempts interrupted and clears their stale display markers, preserving logs and reports. The Claude exec runner performs this recovery automatically after acquiring the lock only when every stale record explicitly says `backend: claude` and `transport: exec`, then starts a fresh attempt. Codex, mixed-host, and records with missing or unknown backend or transport still require explicit recovery. Recovery never reruns work, publishes a result, rolls back edits, or interprets an old report as new evidence.

Before manually retrying, inspect the actual working tree, logs, and prior report. A headless Claude conductor can continue after automatic recovery; it should use the preserved attempt record to recognize the interruption. For Codex native transport, the parent must also stop or await the previously dispatched native agent using the host tools: cancelling a shell waiter cannot cancel a separately hosted subagent. Then rerun the original command as a fresh attempt. Do not replay a late report; native responses are bound to a unique request and its live owner. Recovery does not resume an LLM conversation or guarantee host-managed children have stopped.

## Run a role from a temporary worktree

Use this when the project's checkout must not be touched, for example a bare-clone layout (`<repo>.git` plus worktrees) whose primary worktree has uncommitted work. `run.sh` runs the role in the current directory and exits 2 outside a git work tree, so give it a clean worktree of its own.

This is for interactive or headless conductors outside fanout. A fanout lane conductor already runs in a clean lane worktree and has `SDLC_ROLE=conductor`, so `hooks/block-stray-worktree.sh` denies this worktree add there.

1. Create a detached worktree outside every existing worktree, so nothing is written into the dirty checkout. `--detach` creates no branch.
2. Run the role from it, passing the absolute path of the handoff in the task's home `.sdlc/<task>/` (the `.sdlc/` the conductor already uses for `/board` and `steps.py`).
3. Run the verifier for the same step in the same `$wt` before removal.
4. To keep a builder's edits, commit them on a named branch. Otherwise they are discarded with the worktree.
5. Remove only this recipe's worktree, without `--force`, then its `mktemp` parent.

```sh
wt="$(mktemp -d)/wt"
git -C <any worktree or the bare repo> worktree add --detach "$wt" <commit>
cd "$wt"
run.sh builder <level> /abs/path/.sdlc/<task>/step-N/handoff.md
run.sh verifier <level> /abs/path/.sdlc/<task>/step-N/handoff.md
git -C "$wt" switch -c <branch>          # only to keep the work
git -C "$wt" add -A -- . ':(exclude,glob)**/*.log' ':(exclude,glob)**/.run.lock' ':(exclude,glob)**/*.running' && git -C "$wt" commit -m "<message>"
cd /
git -C <repo> worktree remove "$wt"      # no --force
rmdir "$(dirname "$wt")"
```

The result and `runs.jsonl` land next to the absolute handoff path in the task's home `.sdlc/<task>/`, with nothing to copy back: `run.sh` writes `<role>-<level>.md`, `.log`, `runs.jsonl`, `*.attempt.json`, and, for builder and verifier, `base-sha` beside the handoff it is given. If that home `.sdlc/` sits inside the checkout, it must be git-ignored there, as handoff-format already advises; otherwise the run dirties that checkout.

A builder's edits exist only in `$wt`. They must be committed on a named branch (`git -C "$wt" switch -c <branch>`, then commit) before removal, or they are lost.

Removal uses no `--force`, so a dirty worktree is refused instead of silently discarded. Only the recipe's own worktree is removed. Never prune or remove other worktrees, branches, or stashes.

The recipe does not reuse `SDLC_TMP_WORKTREES`. `run.sh` sets that prefix only inside one role run, under `<toplevel>/.worktrees/tmp/<role>-<pid>` of the checkout it runs in, and deletes it when that run exits. It cannot hold a worktree that must outlive a builder run for the verifier, and it would sit inside the checkout that must not be touched. The run's own stray report does not flag `$wt`, because `$wt` exists before the run's snapshot.

## Long gates

A gate that can outlast the foreground tool timeout (a full test suite, a browser shard run) runs in the background and leaves a receipt:

```sh
python3 <plugin-root>/scripts/gate_lock.py run --receipt /abs/path/gate.receipt.json --timeout <wait-seconds> -- <cmd> > /abs/path/gate.log 2>&1
```

Start it with `run_in_background: true`. Interactive roles may (`hooks/block-background.sh` allows it for them). Then wait for the completion notice. Never poll with `sleep`. When it arrives, read the receipt (`outcome`, `rc`, `wait_ms`, `run_ms`) and the log; the receipt is written last, so a missing receipt means the gate has not finished or died.

`--timeout` bounds only the wait in the admission queue (exit 3, `gate_lock: timeout`), not the command's run time.

To run the gate in the foreground instead, a consumer sets `env.BASH_MAX_TIMEOUT_MS` in its `.claude/settings.json` (for a 90 minute gate, `5400000`). `dispatch.py` sets no environment, so without it a sub-agent keeps the 600000 ms default.

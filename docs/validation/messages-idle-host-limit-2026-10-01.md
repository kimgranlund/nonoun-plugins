# Messages idle-host limit

Date: 2026-10-01. Correction to [Release 0.20.2](release-0.20.2.md) and [Messages live run](messages-live-run.md), which shipped without this limit stated.

## Limit

A subagent, including the messenger, can report only into a parent turn that is still running. It cannot wake an idle host on Claude Code or Codex. A subagent's report is delivered into a running parent turn, and no subagent can start a parent turn that has ended. A Codex user found this when a messenger could not wake a host agent that had gone idle.

## Evidence it was not tested

The live runs covered only an active parent. The Codex parent prompt in [Messages live run](messages-live-run.md) told the parent to wait on the messenger and spawn it again until a report named a claimed message, and the parent's tool calls quoted from its rollout files in the rollout paragraph there (`spawn_agent`, `wait_agent`, `followup_task`, `wait_agent`) held its turn open. The Claude parent ran the messenger in the foreground (`run_in_background: false`). No run let the parent go idle.

## Workaround

Keep the parent in an active turn: on Codex run `/goal` or have the parent wait on the messenger and spawn it again; on Claude Code keep the foreground session working.

## Follow-up

T-0181 adds a blocking `wait` command and T-0182 designs an external watcher; both address this limit.

---
name: port-zombie-sweep
description: >-
  Finds port-squatting dev servers (vite, next, node, workerd, python http.server, and
  similar) that outlived the session, worktree, or agent run that started them, and suggests
  which to kill, grouped by project. Use when a port is "already in use", a dev server picks
  a random port, --strictPort fails, someone asks "what is on port 5173", "kill my stale dev
  servers", "port zombies", or after a batch of agent worktrees finished. Suggests only;
  kills nothing without the user's pick. NOT for CPU-hogging orphan browsers or compilers
  that hold no port (flaky-gates owns those).
user-invocable: true
---

# port-zombie-sweep

A dev server whose owner is gone keeps its port forever. Agent worktrees make this worse:
every `vite dev` or `wrangler dev` started inside a worktree that has since been removed
leaves a listener behind with nobody left to stop it.

Invariant: **MUST NOT kill anything the user has not picked.** The script is read-only.

## 1. Sweep

```sh
~/.claude/skills/port-zombie-sweep/scripts/sweep.py            # grouped by project + binary
~/.claude/skills/port-zombie-sweep/scripts/sweep.py --each     # one row per process
~/.claude/skills/port-zombie-sweep/scripts/sweep.py --all      # include non-dev listeners
~/.claude/skills/port-zombie-sweep/scripts/sweep.py --kill-list  # suggested PIDs only
```

It reads every TCP LISTEN socket on ports 1024 and up, keeps the dev-like processes, and
tags each one:

| Tag | Meaning | Weight |
|---|---|---|
| `cwd-gone` | its working directory was deleted (removed worktree, cleaned tmp dir) | strongest |
| `orphan` | parent is launchd (ppid 1): the terminal or runner that started it is gone | strong |
| `Nd-old` | running for N days | tiebreak only |
| `live` | none of the above: a parent still owns it | never suggested |

`cwd-gone` plus `orphan` is a zombie beyond doubt. `orphan` alone is usually one too, with the
exceptions below.

## 2. Check before suggesting

- **ppid 1 can be a real service.** A LaunchAgent, a Homebrew service, or an app helper also
  has ppid 1. If the cwd is `/` or the command is not a project's dev server, show the full
  `args` (`--each`) and leave it out of the kill list unless the user confirms it is theirs.
- **`live` rows are not zombies**, however old. A 19-day-old vite server with a live parent
  is probably in a tmux pane. Mention it at most.
- **Don't touch listeners under 1024 or system apps** (ControlCenter on 5000/7000, AirPlay,
  and so on). `--all` exists only for looking.

## 3. Suggest, then ask

Report the counts first: how many dev processes, how many suggested. Then give the groups,
biggest win first. Put the kill choice to the user with `AskUserQuestion` (multiSelect).
A good default set of options:

1. All `cwd-gone` groups (recommended, zero risk: their code no longer exists)
2. `orphan` groups in real project paths
3. Specific groups the user names
4. Nothing

Kill with `sweep.py --kill-list | xargs kill` (SIGTERM), or `echo <pids> | xargs kill` for a
subset. Never `kill $pids`: zsh does not word-split, so the whole list becomes one illegal pid. Re-run the sweep after a few seconds. Use `kill -9` only on
PIDs that survive, and only after telling the user. Report what was freed:
🟢 N processes killed, M ports freed; 🟡 any survivors.

## Root cause note

Hundreds of orphaned `workerd` processes under `.worktrees/*/apps/playground` mean something
starts `wrangler dev` / vite with the Cloudflare plugin in agent worktrees and never stops it.
Killing them treats the symptom. Say so, and suggest that the worktree teardown step (or the
test harness) kill its dev server before removing the tree.

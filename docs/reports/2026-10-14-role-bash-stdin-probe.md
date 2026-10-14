# Role Bash stdin probe (T-0548)

Date: 2026-10-14. Host: Claude Code `claude -p --model haiku --dangerously-skip-permissions`, macOS, zsh. Each run printed `$ZSH_EXECUTION_STRING` (the string the host shell ran) to a file.

| Run | Command shape | Host wrapper | Result |
|---|---|---|---|
| no hook | `cat > x; echo LIVE_OK` | `eval '<cmd>' < /dev/null` | finished, 4.5 s |
| no hook, Agent sub-agent | `cat > z; echo SUB_OK` | (same shape) | finished, 9 s |
| no hook, `claude -p` stdin an open pipe | `cat > w; echo PIPE_OK` | (same shape) | finished, 5 s |
| no hook | `cat > hd-out; python3 - <<'PYEOF' ... PYEOF` | `eval '<cmd>'` with no `< /dev/null` | hung; Bash timeout 20 s moved it to the background |
| `close-role-stdin.sh` | same heredoc command | `eval '{ <cmd> } </dev/null'` | printed `HD_OK`, 5.2 s |

Finding: the host closes stdin itself only when the command has no input redirect or heredoc of its own; with one, a bare `cat` reads the inherited stdin and waits for the Bash timeout. The hook's `updatedInput` rewrite, with no `permissionDecision`, is honored and closes stdin for the whole command.

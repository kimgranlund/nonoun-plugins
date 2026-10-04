#!/bin/bash
# Run a command with no inherited Claude Code or SDLC role variables.
args=(-u CLAUDECODE -u CLAUDE_PLUGIN_ROOT -u CLAUDE_PLUGIN_DATA -u CLAUDE_EFFORT -u CLAUDE_PID -u CLAUDE_JOB_DIR)
for v in $(env | sed -n 's/^\(CLAUDE_CODE_[A-Z_0-9]*\)=.*/\1/p; s/^\(SDLC_[A-Z_0-9]*\)=.*/\1/p'); do args+=(-u "$v"); done
exec env "${args[@]}" "$@"

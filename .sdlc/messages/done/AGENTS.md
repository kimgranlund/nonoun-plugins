`done/<receiver>/` holds acknowledged or expired messages, with their `outcome` and, when acked, `ack_time`; the full procedures are in `../AGENTS.md`.
Nothing moves a message out of `done/`: a message never moves backward.
List them: `python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.claude/worktrees/agent-a4f5f90e9874364b7/plugins/sdlc-lite/scripts/messages.py" list --state done`.

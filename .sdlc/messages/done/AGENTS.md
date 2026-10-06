`done/<receiver>/` holds acknowledged or expired messages, with their `outcome` and, when acked, `ack_time`; the full procedures are in `../AGENTS.md`.
Nothing moves a message out of `done/`: a message never moves backward.
List them: `python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout-followups/verify/plugins/sdlc-lite/scripts/messages.py" list --state done`.

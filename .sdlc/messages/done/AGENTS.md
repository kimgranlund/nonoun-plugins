`done/<receiver>/` holds acknowledged or expired messages, with their `outcome` and, when acked, `ack_time`; the full procedures are in `../AGENTS.md`.
Nothing moves a message out of `done/`: a message never moves backward.
List them: `python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/finish/T-0582-t0582/integration/.sdlc/messages/messages-run.py" list --state done`.

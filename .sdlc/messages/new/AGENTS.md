`new/<receiver>/` holds messages sent to that receiver and not yet claimed; the full procedures are in `../AGENTS.md`.
A message leaves `new/` when its receiver claims it with `read` (it moves to `read/`) or when `expire` finds it past its `expires` time (it moves to `done/`).
Claim: `python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/finish/T-0601-t0601/integration/.sdlc/messages/messages-run.py" read <path> --receiver <receiver>`. Expire: `python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/finish/T-0601-t0601/integration/.sdlc/messages/messages-run.py" expire`.

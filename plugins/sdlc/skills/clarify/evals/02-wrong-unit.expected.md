## Goal
A message for an idle harness resumes that harness without a person or a long-lived agent session watching the mailbox.

## Intent
Literal ask: build an agent that watches the mailbox and wakes a harness when a message lands for it while its session is idle.
Level: L3 (lane: full; cost: medium, one new script with process handling; reversible: yes, the script is opt-in)
Deltas:
- category-mismatch: the ask names an agent for a deterministic check -> defaulted: a script, since a new message plus an idle session needs no judgment and a model call per poll adds cost [U] (source: T-0182)
- hidden-scope: the ask does not say who reads the message -> defaulted: the woken session reads it, and the script never claims, moves or reads a message body [U] (source: T-0183)
Do:
1. Add `scripts/supervisor.py` that polls the mailbox, detects an idle session, and starts one unattended wake for it.
2. Add a `supervisor.py selftest` that covers a new message for an idle session and for a busy one.
Non-goals:
- a new agent definition
- changing `messages.py`
- a launchd plist
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/supervisor.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/messages.py selftest` exits 0

## Constraints
The script MUST NOT claim, move or read a message body.

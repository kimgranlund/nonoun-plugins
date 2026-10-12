## Goal
A message for an idle harness resumes that harness without a person or a long-lived agent session watching the mailbox.

## Intent
Literal ask: build an agent that watches the mailbox and wakes a harness when a message lands for it while its session is idle.
Deltas:
- wrong unit: defaulted: the check is deterministic (a new message plus an idle session), so it is a script, not an agent; a model call per poll adds cost and no judgment
- hidden scope: defaulted: the script never claims, moves or reads a message body; the woken session does that
Do: add `scripts/supervisor.py` that polls the mailbox, detects an idle session, and starts one unattended wake for it, with a selftest.
Level: L3 (lane: full; cost: medium, one new script with process handling; reversible: yes, the script is opt-in)
Non-goals: a new agent definition; changing `messages.py`; a launchd plist.
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/supervisor.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/messages.py selftest` exits 0

## Goal
A ticket whose diff touches only docs, records or reports closes on its own checks with no verifier run, and every other ticket still gets one independent verifier.

## Intent
Literal ask: no verifier for a ticket that changes only docs, records or reports.
Deltas:
- conflict: the repo rule is one independent verifier per ticket; defaulted: the skip is a narrow, script-decided exception, and a `verifier:` line in the handoff overrides it
- ambiguity, what counts as docs: defaulted: paths under `docs/`, records under `.sdlc/`, and Markdown outside agent and skill folders; a skill or agent file still needs a verifier
Do: add `scripts/verify_scope.py <base>` that prints `docs-only` when every changed path is docs-only and the docs check passes, and let `tickets.py close` accept a ticket with no verifier result only when it agrees.
Level: L2 (lane: solo; cost: low, one script and one close rule; reversible: yes)
Non-goals: skipping the verifier for any code, skill, agent or hook change; model or effort changes.
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_scope.py selftest` exits 0, with a docs-only case and a one-script case each observed red first
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py selftest` exits 0

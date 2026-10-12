## Goal
A smaller driver runs a plan doc to done with no maintainer hand-fixes, in the cases the live run and rehearsal hit.

## Intent
Literal ask: plan-doc executor: close the live-run gaps (host base, stop record, recover scope, integration branch, verifier record, ticket fields), done when each item has a failing-first selftest, check.sh exits 0, and one more rehearsal plan runs to plan done with no hand step.
Deltas:
- unverifiable done-condition: defaulted: the rehearsal needs a live host run a verifier cannot do, so it moves to the maintainer and the build closes on the selftests
- hidden scope: defaulted: one smallest fix per gap, each with a selftest case observed red first
Do: fix each listed gap in `plan_done.py`, `fanout.py`, `dispatch.py` and the run rules with the smallest change, one selftest case per gap.
Level: L2 (lane: solo; cost: medium, small fixes across four files; reversible: yes)
Non-goals: model or effort rows; the crash drill.
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py selftest` exits 0
- `bash ${CLAUDE_PLUGIN_ROOT}/scripts/check.sh` exits 0
- [owner: maintainer] one more rehearsal plan runs to plan done with no hand step

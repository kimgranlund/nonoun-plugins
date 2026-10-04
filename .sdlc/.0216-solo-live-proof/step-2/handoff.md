## Task goal
A recorded live run shows the `solo` agent delivering a real size-M ticket end to end on Claude Code and Codex. Step 1 recorded both hosts with a direct `claude -p --agent sdlc-lite:solo` launch. Read `.sdlc/0216-solo-live-proof/handoff.md` and `docs/validation/solo-live-run.md` (step 1's record) first. Ticket T-0217 has since merged: a conductor starts solo from Bash with the command in `plugins/sdlc-lite/agents/solo.md`. This step proves that path.

## Step 2: Prove the conductor start path on Claude Code
level: L3

### Read first
- plugins/sdlc-lite/agents/solo.md (the start command and tier table)
- plugins/sdlc-lite/agents/conductor.md (the lane rule and the Lane line)
- docs/validation/solo-live-run.md (step 1: reuse its fixture, brief style and evidence layout)

### Do
Make the smallest change that meets the criteria. This step adds only to docs/validation/solo-live-run.md and docs/validation/solo-live-run/. Do not change any agent, hook or script (report defects as notes). Report blocked instead of looping. Budget about $10; run the arm once and record a failure honestly as a limit.
1. Rebuild the step 1 fixture in a fresh throwaway project outside this repository (the fixture files are under docs/validation/solo-live-run/fixture/; keep the hidden check outside the project dir, never named in any prompt).
2. Start a headless conductor session in that project: `claude -p --plugin-dir <this repo's plugins/sdlc-lite> --agent sdlc-lite:conductor --model sonnet --effort high --dangerously-skip-permissions --output-format stream-json --verbose "<prompt>"` using the same env wrapper step 1 used. The prompt only says to deliver the size-M ticket at `.sdlc/slug-max-length/handoff.md` and gives no solo command; the conductor has to find the lane and the start path from its own agent file. Record from the stream: whether it ran `steps.py lane` and printed `solo`, wrote a `Lane: solo because ...` line, started solo with a Bash `claude -p --agent sdlc-lite:solo` command, whether any Agent-tool spawn of `sdlc-lite:solo` was attempted and denied by the hook, the solo's tier model and effort, the verifier's model, and the conductor's own cost next to the solo's (`footprint.py --session` can read the conductor transcript).
3. After the session run the hidden check on the final tree. Pass or fail, cost and wall time from the records, not from memory.
4. Append a section "Claude Code through a conductor" to docs/validation/solo-live-run.md (lane output, who started solo and with what command, models and effort per session from the records, hidden check result, verifier verdict, cost, wall time, defects as notes, limits), put raw evidence in docs/validation/solo-live-run/conductor/, and update the record's opening paragraph to say step 1 was a direct launch and this section is the conductor start.

### Acceptance criteria
- `grep -q "Claude Code through a conductor" docs/validation/solo-live-run.md`
- `test -d docs/validation/solo-live-run/conductor`
- `grep -q "sdlc-lite:conductor" docs/validation/solo-live-run.md`
- `grep -q -- "--agent sdlc-lite:solo" docs/validation/solo-live-run.md`
- `grep -qi "hidden" docs/validation/solo-live-run.md`
- `git diff --check main -- plugins docs`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `bash plugins/sdlc-lite/scripts/check.sh`

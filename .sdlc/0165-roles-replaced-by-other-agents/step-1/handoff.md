## Task goal
A session in a repository that uses SDLC Lite runs plan, build, and verify work through `run.sh`, and does not substitute another plugin's agent for an SDLC Lite role. A check that failed before the fix passes after it.

## Step 1: Conductor rule against substitute agents, guarded in check.py
level: L2

### Do
In `plugins/sdlc-lite/agents/conductor.md`, section "How you run roles", add this bullet directly after the first bullet, verbatim:

"- Planner, builder, and verifier work runs only through `run.sh`. Never spawn an agent through the Agent tool in their place: not another plugin's builder, planner, reviewer, or checker agent, and not SDLC Lite's own role agents. Other plugins' agents are not substitutes, even when they are listed as proactive."

Change the existing bullet "Every Agent-tool spawn outside run.sh states `model` ..." so it begins "Every other Agent-tool spawn, such as a read-only search helper, states `model`" and keeps the rest of that sentence.

Add a contract check to `plugins/sdlc-lite/scripts/check.py`, next to the other conductor or skill checks, that fails when `agents/conductor.md` lacks the phrase "Other plugins' agents are not substitutes". Give it a built-in negative control in the same style as the existing checks, for example the `fix_lint_bad` check. Confirm the check fails on the old conductor text, then passes.

Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so the generated Codex agents match the new conductor body.

Background: a consumer conductor on 0.18.0 dispatched about 40 builder, planner, and reviewer runs through the Agent tool using other plugins' agents. The current bullet about Agent-tool spawns reads as permission.

### Acceptance criteria
- `grep -qF "Other plugins' agents are not substitutes" plugins/sdlc-lite/agents/conductor.md`
- `grep -qF "not substitutes" plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`

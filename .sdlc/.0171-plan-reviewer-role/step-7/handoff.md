## Task goal
A cross-cutting or risky plan, or any replan, gets an independent semantic review before a builder starts, and a defective plan is rejected before it costs a build.

## Step 7: Loose ends
level: L1

### Do
In `plugins/sdlc-lite/scripts/run.sh`, replace the two-line comment that begins "# Codex: a verifier whose model equals the build's switches to a configured alternate, or else" with a comment that describes both roles, for example: "# Codex: a verifier, or a plan-reviewer, whose model equals the model it reviews (the newest builder's, or the newest planner's) switches to a configured alternate, or else shares that model; resolve then prints a third token "shared" (T-0163, T-0171)." Keep it a comment of at most three lines. Change no code.

### Acceptance criteria
- `grep -qF "a verifier, or a plan-reviewer, whose model equals" plugins/sdlc-lite/scripts/run.sh`
- `! grep -qF "# Codex: a verifier whose model equals the build's switches" plugins/sdlc-lite/scripts/run.sh`
- (guard) `bash -n plugins/sdlc-lite/scripts/run.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

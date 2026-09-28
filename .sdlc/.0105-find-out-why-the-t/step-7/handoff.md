## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Step 7: Loose ends
level: L2
### Do
- In `plugins/sdlc-lite/scripts/run-selftest.sh`, add a case that proves run.sh's heading rule on its own, with a comment line starting `# heading rule:`. The log holds two result events, neither with a `task-notification` origin: first `## Verdict\npass`, then a later `done, see above` with no heading. `verifier L1` must exit 0 and the saved result must hold `## Verdict` and not `done, see above`. Today, removing the heading rule from run.sh leaves the selftest green (step 2 builder and verifier notes); with this case it must go red. Confirm that with a temporary edit of run.sh that you restore, and report it under Checks. Edit only run-selftest.sh.
### Acceptance criteria
- `grep -q '^# heading rule:' plugins/sdlc-lite/scripts/run-selftest.sh && grep -qF 'done, see above' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run-selftest.sh`

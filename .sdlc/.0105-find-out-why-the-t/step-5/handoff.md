## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Step 5: builder and verifier prompts keep gates in the foreground, guarded by check.py
level: L2
### Do
In `plugins/sdlc-lite/agents/builder.md` and `plugins/sdlc-lite/agents/verifier.md`, add a rule containing the exact phrase `never end the turn while background work runs`. The rule says:
- Run gates, tests, and long commands as foreground Bash calls with the Bash `timeout` at 600000 or more.
- Never use `run_in_background` or Monitor.
- Never end the turn while background work runs, because a headless run ends with the turn and the report is lost.

In `plugins/sdlc-lite/scripts/check.py`, add a check that both files contain that exact phrase, with an error naming the file when it is missing.
### Acceptance criteria
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/builder.md`
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/verifier.md`
- `tmp=$(mktemp -d) && mkdir -p "$tmp/plugins" && cp -R plugins/sdlc-lite "$tmp/plugins/sdlc-lite" && cp CLAUDE.md "$tmp/" && sed -i '' 's/never end the turn while background work runs//' "$tmp/plugins/sdlc-lite/agents/verifier.md" && ! python3 "$tmp/plugins/sdlc-lite/scripts/check.py" "$tmp/plugins/sdlc-lite" >/dev/null 2>&1`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`

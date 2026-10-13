## Task goal
Bind each native request to its dispatched profile fingerprint. Reject missing or stale fingerprints in normal responses.

## Step 3: Loose ends
level: L1
guard timeout: 300
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 2.

- In `plugins/sdlc-lite/scripts/codex_exchange.py` line 56, restore the space step 1 dropped: `context ='\n'.join(` becomes `context = '\n'.join(`. Change nothing else.
### Acceptance criteria
- `grep -qF "context = '" plugins/sdlc-lite/scripts/codex_exchange.py && ! grep -qF "context ='" plugins/sdlc-lite/scripts/codex_exchange.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_native_exchange_enforces_the_dispatched_profile_binding CodexTests.test_native_exchange_binding_survives_profile_change_after_dispatch CodexTests.test_native_exchange_failed_response_needs_no_profile_line CodexTests.test_native_exchange_preserves_runner_artifacts`

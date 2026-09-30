## Task goal
The Codex scout is back on `gpt-6-luna` at effort `high`, and the record says why.

## Step 1: Scout L1 on Codex returns to gpt-6-luna
level: L1

### Do
1. In `plugins/sdlc-lite/adapters/codex/models.json`, change the scout L1 entry from `["gpt-6-astra", "high"]` back to `["gpt-6-luna", "high"]`. Change nothing else in the file.
2. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
3. In `docs/codex-role-execution.md`, in the note that starts "Note (2026-09-29, Codex CLI 0.154.0)", replace the sentence beginning "On 2026-09-30 the user set scout L1 to `gpt-6-astra`" through "was the only accepted model in the probes." with: "On 2026-09-30 the scout was briefly moved to `gpt-6-astra` on the strength of those 0.154.0 probes." Then, after the sentence that says `gpt-6.1-sol` is now the configured verifier alternate, add: "The user then returned scout L1 to `gpt-6-luna` at effort `high`, because luna completes live turns on CLI 0.159.2." Keep the rest of the note and its link unchanged.

4. In `docs/codex-role-execution.md`, under "## Default model mapping", change the Scout row from `Astra high` to `Luna high`, so the table matches `models.json`.

### Acceptance criteria
- `grep -q '"scout": {"L1": \["gpt-6-luna", "high"\]}' plugins/sdlc-lite/adapters/codex/models.json`
- `grep -q "gpt-6-luna" plugins/sdlc-lite/adapters/codex/agents/sdlc-scout-l1.toml`
- `grep -q "returned scout L1 to" docs/codex-role-execution.md`
- `! grep -q "was the only accepted model in the probes" docs/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `grep -qE '^\| Scout \| Luna high' docs/codex-role-execution.md`

## Previous attempt
The first verifier failed with a plan defect: the step changed the scout model in `models.json` but not its dependent, the Scout row of the default model mapping table in `docs/codex-role-execution.md`, which still read `Astra high`. Scope and criteria now include that row (Do item 4).

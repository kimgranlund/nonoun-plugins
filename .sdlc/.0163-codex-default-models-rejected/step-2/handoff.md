## Task goal
It is known whether SDLC Lite's Codex defaults work on a ChatGPT account, and a role launched at a default level either runs or fails with a message that names the cause.

## Step 2: Document the shared-model verifier and run the gates
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
1. `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, line 9
   - Replace "switches matching builder/verifier models between Sol and Astra". The new text says the Codex verifier switches to the model `verifier_alternates` in `adapters/codex/models.json` maps the builder's model to.
   - It also says that with no alternate configured, the verifier keeps the builder's model and the runner records `shared_with_builder` in the result header and `runs.jsonl`.
   - Do not touch the Claude tables. `scripts/check.py` checks them against `run.sh`.
2. `docs/codex-role-execution.md`
   - Update the agent count on line 25. It is now 19 agents while no alternate is configured.
   - Update the default model mapping table: Sol becomes Astra, efforts unchanged, Scout stays Luna high.
   - Rewrite the verifier paragraph on line 41 as in item 1.
   - Add a dated note (2026-09-29, Codex CLI 0.154.0): a ChatGPT account rejected `gpt-6-sol` and `gpt-6-luna`, and `gpt-6-astra` was accepted. Say that Luna for scout is kept pending a user decision and that API-key accounts were not tested.
   - Leave the historical live-evidence paragraphs as they are.
3. `plugins/sdlc-lite/HARNESS-NOTES.md`
   - Line 19: fix the agent count and alternate-profile wording.
   - Line 27: replace "switch between Sol and Astra" with the same configured-alternate / shared rule.
4. Run every gate below and fix any red that step 1 introduced.
### Acceptance criteria
- `! grep -qF "between Sol and Astra" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF verifier_alternates plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF verifier_alternates docs/codex-role-execution.md`
- `! grep -qF "| Sol " docs/codex-role-execution.md`
- `grep -qF "ChatGPT account" docs/codex-role-execution.md`
- `! grep -qF "22 project agent definitions" docs/codex-role-execution.md`
- `! grep -qF "between Sol and Astra" plugins/sdlc-lite/HARNESS-NOTES.md`
- `! grep -qF "22 namespaced agents" plugins/sdlc-lite/HARNESS-NOTES.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check`

## Task goal
Each Codex level runs on the model tier that mirrors its Claude level, with the same effort, and Codex verifier independence mirrors the Claude rule.

## Step 1: Mirror the Claude tiers in the Codex mapping
level: L2

### Do
1. Replace the role entries in `plugins/sdlc-lite/adapters/codex/models.json` with exactly this mapping, and keep the JSON valid and each role on one line as now:
   - builder: L1 `gpt-6-luna` low, L2 `gpt-6.1-sol` low, L3 `gpt-6.1-sol` high, L4 `gpt-6.1-sol` xhigh, L5 `gpt-6-astra` xhigh
   - planner: L1 `gpt-6-luna` medium, L2 `gpt-6.1-sol` medium, L3 `gpt-6-astra` xhigh
   - verifier: L1 `gpt-6-luna` medium, L2 `gpt-6-luna` high, L3 `gpt-6-astra` xhigh
   - researcher: L1 `gpt-6-luna` medium, L2 `gpt-6.1-sol` medium, L3 `gpt-6.1-sol` high
   - architect: L1 `gpt-6-astra` high
   - scout: L1 `gpt-5.6-terra` low
   - archaeologist: L1 `gpt-6-luna` medium
   - filer: L1 `gpt-6-luna` medium
   - conductor: L1 `gpt-6-astra` medium (unchanged)
   - `verifier_alternates`: `{"gpt-6-luna": "gpt-6.1-sol", "gpt-6-astra": "gpt-6.1-sol"}`
2. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
3. Update `plugins/sdlc-lite/scripts/codex-selftest.py` so its alternate-selection tests still prove both an empty and a configured alternate map against the new mapping: the verifier L1 test writes a builder result whose header names `gpt-6-luna` (the model verifier L1 now resolves to), and its expectations name `gpt-6-luna`, `medium`, and the alternate, keeping every existing negative control. Change no test that does not depend on the mapping.
4. In `docs/references/codex-role-execution.md`, replace the default-model table under "## Default model mapping" with the new mapping, one row per role as now, writing model names in the form `Sol 6.1`, `Astra`, `Luna`, `Terra 5.6` followed by the effort. Add to the dated note that starts "Note (2026-09-29, Codex CLI 0.154.0)" this sentence: "On 2026-09-30 the user mirrored the Claude tiers: Opus maps to `gpt-6.1-sol`, Fable to `gpt-6-astra`, Sonnet to `gpt-6-luna`, Haiku to `gpt-5.6-terra`, with the Claude effort, and verifier alternates mirror the Claude family rule." Leave the rest of the note unchanged.

### Acceptance criteria
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import codex_roles as c; S='gpt-6.1-sol'; A='gpt-6-astra'; L='gpt-6-luna'; want={'builder':{'L1':[L,'low'],'L2':[S,'low'],'L3':[S,'high'],'L4':[S,'xhigh'],'L5':[A,'xhigh']},'planner':{'L1':[L,'medium'],'L2':[S,'medium'],'L3':[A,'xhigh']},'verifier':{'L1':[L,'medium'],'L2':[L,'high'],'L3':[A,'xhigh']},'researcher':{'L1':[L,'medium'],'L2':[S,'medium'],'L3':[S,'high']},'architect':{'L1':[A,'high']},'scout':{'L1':['gpt-5.6-terra','low']},'archaeologist':{'L1':[L,'medium']},'filer':{'L1':[L,'medium']},'conductor':{'L1':[A,'medium']}}; assert c.models()==want, c.models()"`
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import codex_roles as c; assert c.verifier_alternates()=={'gpt-6-luna':'gpt-6.1-sol','gpt-6-astra':'gpt-6.1-sol'}, c.verifier_alternates()"`
- `grep -qF "Terra 5.6 low" docs/references/codex-role-execution.md`
- `grep -qF "the user mirrored the Claude tiers" docs/references/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Task goal
The Codex planner, builder, and verifier levels follow the role-based allocation the Codex session proposed and the user adopted; every other Codex role keeps the Claude-tier mirror.

## Step 1: Role-based Codex allocation for planner, builder, and verifier
level: L2

### Do
1. In `plugins/sdlc-lite/adapters/codex/models.json`, change only the builder, planner, and verifier entries to:
   - builder: L1 `gpt-6-luna` low, L2 `gpt-6.1-sol` low, L3 `gpt-6.1-sol` medium, L4 `gpt-6.1-sol` high, L5 `gpt-6.1-sol` xhigh
   - planner: L1 `gpt-6.1-sol` medium, L2 `gpt-6.1-sol` high, L3 `gpt-6-astra` high
   - verifier: L1 `gpt-6-luna` low, L2 `gpt-6-luna` medium, L3 `gpt-6-astra` high
   Leave researcher, architect, scout, archaeologist, filer, conductor, and `verifier_alternates` exactly as they are.
2. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
3. Update `plugins/sdlc-lite/scripts/codex-selftest.py` wherever a test depends on the verifier L1 effort (it is now `low`, not `medium`) or on the builder or verifier models changed above, keeping both the empty and the configured alternate map cases and every negative control. Change no test that does not depend on the mapping.
4. In `docs/references/codex-role-execution.md`, update the default-model table for the builder, planner, and verifier rows to the new values, in the table's existing style. Add to the dated note that starts "Note (2026-09-29, Codex CLI 0.154.0)": "Later on 2026-09-30 the user adopted a role-based allocation for planner, builder, and verifier, proposed by the Codex session, replacing the Claude-tier mirror for those roles. It is a proposed setting, not a demonstrated performance equivalent." Leave the rest unchanged.

### Acceptance criteria
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import codex_roles as c; S='gpt-6.1-sol'; A='gpt-6-astra'; L='gpt-6-luna'; m=c.models(); assert m['builder']=={'L1':[L,'low'],'L2':[S,'low'],'L3':[S,'medium'],'L4':[S,'high'],'L5':[S,'xhigh']}, m['builder']; assert m['planner']=={'L1':[S,'medium'],'L2':[S,'high'],'L3':[A,'high']}, m['planner']; assert m['verifier']=={'L1':[L,'low'],'L2':[L,'medium'],'L3':[A,'high']}, m['verifier']; assert m['researcher']=={'L1':[L,'medium'],'L2':[S,'medium'],'L3':[S,'high']}, m['researcher']; assert m['architect']=={'L1':[A,'high']} and m['scout']=={'L1':['gpt-5.6-terra','low']} and m['archaeologist']=={'L1':[L,'medium']} and m['filer']=={'L1':[L,'medium']} and m['conductor']=={'L1':[A,'medium']}"`
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import codex_roles as c; assert c.verifier_alternates()=={'gpt-6-luna':'gpt-6.1-sol','gpt-6-astra':'gpt-6.1-sol'}, c.verifier_alternates()"`
- `grep -qF "adopted a role-based allocation" docs/references/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Goal
Current docs describe the Codex alternate verifier map, agent count, and scout model as they are now; dated records stay history.

## Context
The Codex session reviewed 070b98a on 2026-09-30 and found four stale statements after the role-based allocation. The author confirmed each. Current facts: `verifier_alternates` is `{"gpt-6-luna": "gpt-6.1-sol", "gpt-6-astra": "gpt-6.1-sol"}`, `codex_roles.py install` with the default configuration installs 22 agents (19 base plus three alternate verifier profiles, one per verifier level whose model has an alternates entry), and the Codex scout is `gpt-5.6-terra` low.

## Constraints
Docs only. Dated validation records are corrected by an added dated line and are never rewritten.

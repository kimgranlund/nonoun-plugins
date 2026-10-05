## Goal
The Codex planner, builder, and verifier levels follow the role-based allocation the Codex session proposed and the user adopted; every other Codex role keeps the Claude-tier mirror.

## Context
User decision, 2026-09-30: adopt the allocation in the Codex session's proposal (planner L1 `gpt-6.1-sol` medium, L2 `gpt-6.1-sol` high, L3 `gpt-6-astra` high; builder L1 `gpt-6-luna` low, L2 `gpt-6.1-sol` low, L3 `gpt-6.1-sol` medium, L4 `gpt-6.1-sol` high, L5 `gpt-6.1-sol` xhigh; verifier L1 `gpt-6-luna` low, L2 `gpt-6-luna` medium, L3 `gpt-6-astra` high). It replaces the Claude-tier mirror for those three roles. Researcher, architect, scout, archaeologist, filer, and conductor keep the mirror set earlier the same day. `verifier_alternates` stays `{"gpt-6-luna": "gpt-6.1-sol", "gpt-6-astra": "gpt-6.1-sol"}`. The rubric routes builder L1 or L2 to verifier L1, L3 to L2, and L4 or L5 to L3, so the normal pairings are: L1 Luna low then Sol 6.1 low (swapped, same model as the builder), L2 Sol low then Luna low, L3 Sol medium then Luna medium, L4 and L5 Sol then Astra high. These are proposed settings, not demonstrated performance equivalents. Every model and effort pair was probed live on CLI 0.159.2 the same day (`docs/reports/codex-tier-mirror-2026-09-30.md`).

## Constraints
`scripts/run.sh` and every Claude model and effort stay unchanged. Only the Codex mapping, its generated agents, the Codex selftest fixtures, and `docs/codex-role-execution.md` change.

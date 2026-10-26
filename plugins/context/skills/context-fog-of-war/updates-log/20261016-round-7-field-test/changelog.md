---
date: 2026-10-16
slug: round-7-field-test
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L2 (0303-solo-L2)
    model: claude-opus-5-5
    did: ran the skill unaided, including the contract audit link mode, on agent-ui live round 7 (15 runs) and recorded these notes in that round's report
  - role: verifier
    agent: sdlc-lite:verifier-L2 (0303-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification of the round 7 report, verdict pass
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote this entry from the verified report
project: agent-ui (nonoun), live round 7, report .sdlc/evals/rounds/2026-10-16-r7-fails/report.md, fog report 1e10193208c4414271381d65
verification: field test verified by an independent verifier (L2 pass); findings only, no skill file changed
backup: none (no skill file changed)
---

# 2026-10-16: field test of the checklist and the contract audit link mode (round 7)

## Verified in the field
- The checklist ran unaided to a published report and a why-and-fix table.
- `audit.py link` named the guidance homes for both new clusters once the mapping listed the repair text and the tool definition.

## Open
- **Provider-error turns:** the checklist has no step for excluding them from a bundle. The ticket said to drop the usage-limit lines. Blanking them in an ingested copy kept the line numbers, and the ingest skipped the blank lines (87 envelopes from 96 lines). Applied in 20261016-open-items.
- **Audit mapping coverage:** the reused contract-audit mapping did not list the producer's repair text or the tool definition. `link --finding f1` matched only CardTable entity hits until those two surfaces were added. Contract-audit step 4 names repair messages as surfaces, but the reused mapping predates that. Applied in 20261016-open-items.
- **`include` type:** `audit.py` crashed with `TypeError: unhashable type: 'list'` when a surface's `include` was a list. `contract-audit.md` says "`include` and `exclude` regexes", which reads as a list. A single regex string works. Applied in 20261016-open-items.
- **`link` phrase match:** the five-word phrase match runs over the whole file, not the mapped statements. A finding whose `target` names a path under `packages/agent-ui/a2ui/src/agent/` matches the `import.meta.glob` lines `site/pages/agent-admin-libraries.ts:28` and `:70` on every query, f4 included. Applied in 20261016-open-items.
- **`link` input:** `link --finding` ranks by the finding's own words. It reached the three guidance homes in A only once f1's hypothesis quoted them, so a finding should quote the guidance it suspects. Applied in 20261016-open-items.
- **Truncation:** the max_tokens question came from the ticket. The `truncation` detector cannot see a stop at the token cap when the trace records no stop reason. The skill could name `outputTokens` equal to the request's `max_tokens` as the evidence to map. Applied in 20261016-open-items.

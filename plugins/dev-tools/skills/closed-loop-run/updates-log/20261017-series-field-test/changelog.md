---
date: 2026-10-17
slug: series-field-test
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L2
    model: claude-opus-5-5
    did: applied references/experiment-series.md to one full paid cycle of a generative UI runtime (87 cases, three models) and wrote this entry
project: a generative UI runtime's live evaluation series, the full cycle after a round of fixes
verification: pass (T-0326 verifier, sonnet L2, 2026-10-17)
backup: none (no skill file changed)
---

# 2026-10-17: field test of the experiment-series reference on a full cycle

## Verified in the field
- Section 3 churn: the totals were unchanged (77 of 87 both cycles) while 6 cases turned green and 6 turned red; the transition table named every pass to fail case with its cluster, as the reference predicts.
- Section 4: per-fix mechanism metrics separated a fix that never met its condition ("not exercised", 3 of 8 fixes) from one that worked.
- Section 1: comparing prompt section digests between cycles narrowed one regression to the only guidance that changed.

## Open
- **A changed case inside a full cycle.** Section 1 says a changed set is a new set, but a fix to one scenario (3 of 87 cases) is common. The reference could say: keep the unchanged cases comparable, mark the changed ones as a new baseline, and report both counts.
- **Mechanism met, outcome regressed.** A forced-retry fix did what it said on 7 of 7 rounds, yet saved 0 turns, and its owner's revisit condition (halts rising) was met. The verdict set in section 4 has no "mechanism fixed live, outcome regressed" verdict; the report had to write both.
- **Fixed by noise.** Four cases went from fail to pass with no fix exercised. Section 3 says to name the fix or say none applies; a short rule ("a fail to pass with no fix whose condition occurred is noise; keep its ticket open") would stop a reader from counting them as fixes.
